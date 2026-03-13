from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.logger import logger
from core.permissions import IsAdminKotizo
from cotisations.models import Cotisation, Signalement
from paiements.models import Transaction, DemandeRemboursement
from users.models import VerificationIdentite, DemandeBusinessLevel, Sanction, AlerteFraude
from agent_ia.models import TicketSupport
from .serializers import (
    AdminUserSerializer, AdminVerificationSerializer,
    AdminCotisationSerializer, AdminTransactionSerializer,
    AdminSanctionSerializer, AdminAlerteFraudeSerializer,
    AdminTicketSerializer,
)

User = get_user_model()


class DashboardView(APIView):
    permission_classes = [IsAdminKotizo]

    def get(self, request):
        aujourd_hui = timezone.now().date()
        return Response({
            'users': {
                'total': User.objects.count(),
                'basique': User.objects.filter(niveau='basique').count(),
                'verifie': User.objects.filter(niveau='verifie').count(),
                'business': User.objects.filter(niveau='business').count(),
                'nouveaux_aujourd_hui': User.objects.filter(date_inscription__date=aujourd_hui).count(),
            },
            'cotisations': {
                'total': Cotisation.objects.count(),
                'actives': Cotisation.objects.filter(statut='active').count(),
                'completes': Cotisation.objects.filter(statut='complete').count(),
                'suspendues': Cotisation.objects.filter(statut='suspendue').count(),
            },
            'transactions': {
                'total_aujourd_hui': Transaction.objects.filter(
                    date_creation__date=aujourd_hui, statut='complete'
                ).count(),
                'volume_aujourd_hui': sum(
                    t.montant for t in Transaction.objects.filter(
                        date_creation__date=aujourd_hui,
                        statut='complete',
                        type_transaction='payin',
                    )
                ),
            },
            'alertes': {
                'fraude_nouvelles': AlerteFraude.objects.filter(statut='nouvelle').count(),
                'verifications_en_attente': VerificationIdentite.objects.filter(statut='en_attente').count(),
                'tickets_ouverts': TicketSupport.objects.filter(statut='ouvert').count(),
                'signalements_en_attente': Signalement.objects.filter(statut='en_attente').count(),
            },
        })


class AdminUsersView(APIView):
    permission_classes = [IsAdminKotizo]

    def get(self, request):
        users = User.objects.all().order_by('-date_inscription')
        niveau = request.query_params.get('niveau')
        search = request.query_params.get('search')
        if niveau:
            users = users.filter(niveau=niveau)
        if search:
            users = users.filter(email__icontains=search) | users.filter(nom__icontains=search)
        return Response(AdminUserSerializer(users, many=True).data)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminKotizo]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            return Response(AdminUserSerializer(user).data)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            champs_autorises = ['is_active', 'niveau']
            for champ in champs_autorises:
                if champ in request.data:
                    setattr(user, champ, request.data[champ])
            user.save()
            logger.info(f'User modifie par admin', user_id=str(user_id))
            return Response(AdminUserSerializer(user).data)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)


class AdminVerificationsView(APIView):
    permission_classes = [IsAdminKotizo]

    def get(self, request):
        verifs = VerificationIdentite.objects.all().order_by('-date_soumission')
        statut = request.query_params.get('statut')
        if statut:
            verifs = verifs.filter(statut=statut)
        return Response(AdminVerificationSerializer(verifs, many=True).data)


class AdminVerificationActionView(APIView):
    permission_classes = [IsAdminKotizo]

    def post(self, request, verif_id):
        try:
            verif = VerificationIdentite.objects.get(id=verif_id)
        except VerificationIdentite.DoesNotExist:
            return Response({'error': 'Verification introuvable'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        note = request.data.get('note', '')

        if action == 'approuver':
            verif.statut = 'approuve'
            verif.note_admin = note
            verif.date_traitement = timezone.now()
            verif.save()
            verif.user.niveau = 'verifie'
            verif.user.save(update_fields=['niveau'])
            from notifications.tasks import envoyer_notification_verification
            envoyer_notification_verification.delay(str(verif.user.id), True)
            logger.info(f'Verification approuvee user {verif.user.id}')

        elif action == 'rejeter':
            verif.statut = 'rejete'
            verif.note_admin = note
            verif.date_traitement = timezone.now()
            verif.save()
            from notifications.tasks import envoyer_notification_verification
            envoyer_notification_verification.delay(str(verif.user.id), False)
            logger.info(f'Verification rejetee user {verif.user.id}')
        else:
            return Response({'error': 'Action invalide'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'Verification {action}e'})


class AdminTransactionsView(APIView):
    permission_classes = [IsAdminKotizo]

    def get(self, request):
        transactions = Transaction.objects.all().order_by('-date_creation')
        type_t = request.query_params.get('type')
        statut = request.query_params.get('statut')
        if type_t:
            transactions = transactions.filter(type_transaction=type_t)
        if statut:
            transactions = transactions.filter(statut=statut)
        return Response(AdminTransactionSerializer(transactions, many=True).data)


class AdminAlertesView(APIView):
    permission_classes = [IsAdminKotizo]

    def get(self, request):
        alertes = AlerteFraude.objects.all().order_by('-date_creation')
        statut = request.query_params.get('statut', 'nouvelle')
        alertes = alertes.filter(statut=statut)
        return Response(AdminAlerteFraudeSerializer(alertes, many=True).data)


class AdminSanctionView(APIView):
    permission_classes = [IsAdminKotizo]

    def post(self, request):
        user_id = request.data.get('user_id')
        niveau = request.data.get('niveau')
        raison = request.data.get('raison')
        date_fin = request.data.get('date_fin')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)

        sanction = Sanction.objects.create(
            user=user,
            niveau=niveau,
            raison=raison,
            appliquee_par=request.user,
            date_fin=date_fin,
        )

        if niveau >= 4:
            user.is_active = False
            user.save(update_fields=['is_active'])

        if niveau >= 3:
            user.niveau = 'basique'
            user.save(update_fields=['niveau'])

        from notifications.tasks import envoyer_notification_sanction
        envoyer_notification_sanction.delay(str(user.id), niveau, raison)

        logger.warning(f'Sanction niveau {niveau} appliquee user {user_id}')
        return Response({'message': 'Sanction appliquee'}, status=status.HTTP_201_CREATED)


class AdminTicketsView(APIView):
    permission_classes = [IsAdminKotizo]

    def get(self, request):
        tickets = TicketSupport.objects.all().order_by('-date_creation')
        statut = request.query_params.get('statut')
        if statut:
            tickets = tickets.filter(statut=statut)
        return Response(AdminTicketSerializer(tickets, many=True).data)


class AdminTicketActionView(APIView):
    permission_classes = [IsAdminKotizo]

    def patch(self, request, ticket_id):
        try:
            ticket = TicketSupport.objects.get(id=ticket_id)
        except TicketSupport.DoesNotExist:
            return Response({'error': 'Ticket introuvable'}, status=status.HTTP_404_NOT_FOUND)

        statut = request.data.get('statut')
        note = request.data.get('note_admin', '')

        if statut:
            ticket.statut = statut
        if note:
            ticket.note_admin = note
        if statut == 'resolu':
            ticket.date_resolution = timezone.now()

        ticket.save()
        return Response(AdminTicketSerializer(ticket).data)