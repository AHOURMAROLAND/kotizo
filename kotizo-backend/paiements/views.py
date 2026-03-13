from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
import json
from core.logger import logger
from cotisations.models import Cotisation, Participation
from .models import Transaction, DemandeRemboursement
from .serializers import TransactionSerializer, DemandeRemboursementSerializer
from .utils import (
    creer_invoice_payin, verifier_hash_webhook,
    confirmer_invoice, verifier_statut_payout
)
from cotisations.utils import calculer_frais_kotizo


class InitierPaiementCotisationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        cotisation = get_object_or_404(Cotisation, slug=slug, statut='active')
        participation = get_object_or_404(
            Participation,
            cotisation=cotisation,
            participant=request.user,
            statut='en_attente',
        )

        frais = calculer_frais_kotizo(cotisation.montant_unitaire)
        montant_total = int(cotisation.montant_unitaire) + frais

        transaction = Transaction.objects.create(
            user=request.user,
            type_transaction='payin',
            source='cotisation',
            source_id=str(cotisation.id),
            montant=montant_total,
            frais_kotizo=frais,
            statut='initie',
        )

        result = creer_invoice_payin(
            montant=montant_total,
            description=f'Cotisation : {cotisation.nom}',
            token_reference=str(transaction.id),
            return_url=f'kotizo://paiement-success?transaction={transaction.id}',
            cancel_url='kotizo://paiement-cancel',
            ipn_url='https://api.kotizo.app/api/paiements/webhook/payin/',
        )

        if result.get('response_code') != '00':
            transaction.statut = 'echoue'
            transaction.save()
            logger.paiement('Echec creation invoice', user_id=str(request.user.id), statut='echoue')
            return Response({'error': 'Erreur creation paiement'}, status=status.HTTP_502_BAD_GATEWAY)

        invoice_token = result.get('token')
        payment_url = result.get('response_text')

        transaction.paydunya_token = invoice_token
        transaction.statut = 'en_attente'
        transaction.save()

        participation.paydunya_token = invoice_token
        participation.save()

        logger.paiement('Invoice cree', user_id=str(request.user.id), montant=montant_total, statut='en_attente')

        return Response({
            'payment_url': payment_url,
            'invoice_token': invoice_token,
            'montant': montant_total,
            'frais_kotizo': frais,
        })


@method_decorator(csrf_exempt, name='dispatch')
class WebhookPayinView(APIView):
    permission_classes = []

    def post(self, request):
        logger.webhook('Webhook PayIn recu', source='paydunya')

        hash_recu = request.headers.get('X-PAYDUNYA-SIGNATURE', '')
        hash_attendu = verifier_hash_webhook(settings.PAYDUNYA_MASTER_KEY)

        if hash_recu != hash_attendu:
            logger.fraude('Hash webhook invalide')
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
            transaction = Transaction.objects.get(paydunya_token=invoice_token)
        except Transaction.DoesNotExist:
            return Response(status=404)

        transaction.webhook_recu = True
        transaction.webhook_data = data

        if invoice_status == 'completed':
            transaction.statut = 'complete'
            transaction.date_completion = timezone.now()
            transaction.save()
            logger.paiement('Paiement confirme webhook', user_id=str(transaction.user.id), statut='complete')
            from .tasks import traiter_paiement_confirme
            traiter_paiement_confirme.delay(str(transaction.id))
        else:
            transaction.statut = 'echoue'
            transaction.save()
            logger.paiement('Paiement echoue webhook', user_id=str(transaction.user.id), statut='echoue')

        return Response({'status': 'ok'})


@method_decorator(csrf_exempt, name='dispatch')
class WebhookPayoutView(APIView):
    permission_classes = []

    def post(self, request):
        logger.webhook('Webhook PayOut recu', source='paydunya')

        try:
            data = json.loads(request.body)
        except Exception:
            return Response(status=400)

        reference = data.get('reference_id')
        payout_status = data.get('status')

        if not reference:
            return Response(status=400)

        try:
            transaction = Transaction.objects.get(id=reference, type_transaction='payout')
        except Transaction.DoesNotExist:
            return Response(status=404)

        if payout_status == 'SUCCESS':
            transaction.statut = 'complete'
            transaction.date_completion = timezone.now()
            transaction.save()
            logger.paiement('PayOut confirme', user_id=str(transaction.user.id), statut='complete')
        else:
            transaction.statut = 'echoue'
            transaction.save()
            logger.paiement('PayOut echoue', user_id=str(transaction.user.id), statut='echoue')

        return Response({'status': 'ok'})


class HistoriqueTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)
        return Response(TransactionSerializer(transactions, many=True).data)


class DemandeRemboursementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DemandeRemboursementSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        transaction = serializer.validated_data['transaction']
        if transaction.user != request.user:
            return Response({'error': 'Acces refuse'}, status=status.HTTP_403_FORBIDDEN)

        if DemandeRemboursement.objects.filter(transaction=transaction).exists():
            return Response({'error': 'Demande deja soumise pour cette transaction'}, status=status.HTTP_400_BAD_REQUEST)

        demande = serializer.save(user=request.user)
        logger.info(f'Demande remboursement creee', user_id=str(request.user.id))
        return Response(DemandeRemboursementSerializer(demande).data, status=status.HTTP_201_CREATED)