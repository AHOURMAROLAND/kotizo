from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from core.logger import logger
from paiements.utils import creer_invoice_payin, verifier_hash_webhook
from paiements.models import Transaction
from cotisations.utils import calculer_frais_kotizo, detecter_operateur
from .models import QuickPay
from .serializers import QuickPayCreateSerializer, QuickPaySerializer
from .utils import generer_code_quickpay
from django.conf import settings
import json


class QuickPayCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuickPayCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        operateur = detecter_operateur(serializer.validated_data['numero_receveur'])
        quickpay = serializer.save(
            createur=request.user,
            code=generer_code_quickpay(),
            operateur_receveur=operateur,
            date_expiration=timezone.now() + timedelta(hours=1),
        )

        logger.info(f'QuickPay cree', user_id=str(request.user.id))
        return Response(QuickPaySerializer(quickpay).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        quickpays = QuickPay.objects.filter(createur=request.user)
        return Response(QuickPaySerializer(quickpays, many=True).data)


class QuickPayDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, code):
        quickpay = get_object_or_404(QuickPay, code=code)

        if quickpay.statut == 'expire':
            return Response({'error': 'Ce lien Quick Pay a expire'}, status=status.HTTP_410_GONE)
        if quickpay.statut == 'paye':
            return Response({'error': 'Ce paiement a deja ete effectue'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(QuickPaySerializer(quickpay).data)


class InitierPaiementQuickPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        quickpay = get_object_or_404(QuickPay, code=code, statut='actif')

        if quickpay.createur == request.user:
            return Response({'error': 'Vous ne pouvez pas payer votre propre Quick Pay'}, status=status.HTTP_400_BAD_REQUEST)

        if quickpay.date_expiration <= timezone.now():
            quickpay.statut = 'expire'
            quickpay.save()
            return Response({'error': 'Ce lien Quick Pay a expire'}, status=status.HTTP_410_GONE)

        frais = calculer_frais_kotizo(quickpay.montant)
        montant_total = int(quickpay.montant) + frais

        transaction = Transaction.objects.create(
            user=request.user,
            type_transaction='payin',
            source='quickpay',
            source_id=str(quickpay.id),
            montant=montant_total,
            frais_kotizo=frais,
            statut='initie',
        )

        result = creer_invoice_payin(
            montant=montant_total,
            description=f'Quick Pay : {quickpay.description or quickpay.code}',
            token_reference=str(transaction.id),
            return_url=f'kotizo://quickpay-success?transaction={transaction.id}',
            cancel_url='kotizo://paiement-cancel',
            ipn_url='https://api.kotizo.app/api/quickpay/webhook/',
        )

        if result.get('response_code') != '00':
            transaction.statut = 'echoue'
            transaction.save()
            return Response({'error': 'Erreur creation paiement'}, status=status.HTTP_502_BAD_GATEWAY)

        invoice_token = result.get('token')
        payment_url = result.get('response_text')

        transaction.paydunya_token = invoice_token
        transaction.statut = 'en_attente'
        transaction.save()

        quickpay.paydunya_token = invoice_token
        quickpay.save()

        logger.paiement('QuickPay invoice cree', user_id=str(request.user.id), montant=montant_total)

        return Response({
            'payment_url': payment_url,
            'invoice_token': invoice_token,
            'montant': montant_total,
            'frais_kotizo': frais,
        })


@method_decorator(csrf_exempt, name='dispatch')
class WebhookQuickPayView(APIView):
    permission_classes = []

    def post(self, request):
        logger.webhook('Webhook QuickPay recu', source='paydunya')

        hash_recu = request.headers.get('X-PAYDUNYA-SIGNATURE', '')
        hash_attendu = verifier_hash_webhook(settings.PAYDUNYA_MASTER_KEY)

        if hash_recu != hash_attendu:
            logger.fraude('Hash webhook QuickPay invalide')
            return Response(status=403)

        try:
            data = json.loads(request.body)
        except Exception:
            return Response(status=400)

        invoice_token = data.get('data', {}).get('invoice', {}).get('token')
        invoice_status = data.get('data', {}).get('invoice', {}).get('status')

        if not invoice_token:
            return Response(status=400)

        try:
            quickpay = QuickPay.objects.get(paydunya_token=invoice_token)
            transaction = Transaction.objects.get(paydunya_token=invoice_token)
        except (QuickPay.DoesNotExist, Transaction.DoesNotExist):
            return Response(status=404)

        if invoice_status == 'completed':
            transaction.statut = 'complete'
            transaction.date_completion = timezone.now()
            transaction.save()

            quickpay.statut = 'paye'
            quickpay.date_paiement = timezone.now()
            quickpay.payeur = transaction.user
            quickpay.save()

            logger.paiement('QuickPay paye', user_id=str(transaction.user.id), statut='complete')

            from .tasks import traiter_payout_quickpay
            traiter_payout_quickpay.delay(str(quickpay.id))
        else:
            transaction.statut = 'echoue'
            transaction.save()

        return Response({'status': 'ok'})