from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.logger import KotizoLogger
from users.models import User, SessionDevice
from users.serializers import (
    UserProfileSerializer,
    UserPublicSerializer,
    ThemeSerializer,
    VerificationCNISerializer,
    SessionSerializer,
)

logger = KotizoLogger('users.views')


class MonProfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data,
            partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class ThemeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ThemeSerializer(
            request.user, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'message': 'Theme mis a jour.', **serializer.data})


class ProfilPublicView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, is_active=True, statut='actif')
            serializer = UserPublicSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)


class VerificationIdentiteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.identite_verifiee:
            return Response({'error': 'Identite deja verifiee.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.statut_verification == 'en_attente':
            return Response({'error': 'Dossier deja en attente de validation.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = VerificationCNISerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user.photo_cni_recto = serializer.validated_data['photo_recto']
        user.photo_cni_verso = serializer.validated_data['photo_verso']
        user.numero_cni_hash = serializer.validated_data['numero_carte']
        user.statut_verification = 'en_attente'
        user.save()

        from notifications.models import Notification
        Notification.objects.create(
            user=user,
            type_notification='systeme',
            titre='Dossier recu',
            message='Votre dossier de verification est en cours d examen (24-48h).'
        )

        logger.info('verification_soumise', {'user_id': str(user.id)})

        return Response({'message': 'Dossier soumis avec succes. Reponse sous 24-48h.'})


class SessionsActivesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = SessionDevice.objects.filter(
            user=request.user, is_active=True
        ).order_by('-date_connexion')
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)


class RevoquerSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, session_id):
        try:
            session = SessionDevice.objects.get(
                id=session_id, user=request.user
            )
            session.is_active = False
            session.save()
            return Response({'message': 'Session revoquee.'})
        except SessionDevice.DoesNotExist:
            return Response({'error': 'Session introuvable.'}, status=status.HTTP_404_NOT_FOUND)


class DemandeBusinessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.niveau == 'business':
            return Response({'error': 'Vous etes deja Business.'}, status=status.HTTP_400_BAD_REQUEST)

        nom_entreprise = request.data.get('nom_entreprise', '')
        secteur = request.data.get('secteur', '')
        description = request.data.get('description', '')
        volume = request.data.get('volume_mensuel', '')
        tel_pro = request.data.get('telephone_pro', '')

        if not all([nom_entreprise, secteur, description]):
            return Response({'error': 'Champs obligatoires manquants.'}, status=status.HTTP_400_BAD_REQUEST)

        from core.email_router import envoyer_email
        envoyer_email(
            'admin@kotizo.app',
            f'Demande Business — @{user.pseudo}',
            f'<p>Utilisateur : @{user.pseudo} ({user.email})</p>'
            f'<p>Entreprise : {nom_entreprise}</p>'
            f'<p>Secteur : {secteur}</p>'
            f'<p>Description : {description}</p>'
            f'<p>Volume mensuel : {volume}</p>'
            f'<p>Tel pro : {tel_pro}</p>'
        )

        logger.info('demande_business', {'user_id': str(user.id)})
        return Response({'message': 'Demande envoyee. Reponse sous 2-5 jours.'})


class ReclamationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        type_probleme = request.data.get('type_probleme', '')
        description = request.data.get('description', '')

        if not type_probleme or not description:
            return Response({'error': 'Type et description obligatoires.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(description) < 20:
            return Response({'error': 'Description trop courte (min 20 chars).'}, status=status.HTTP_400_BAD_REQUEST)

        from core.email_router import envoyer_email
        envoyer_email(
            'support@kotizo.app',
            f'Reclamation — @{request.user.pseudo} — {type_probleme}',
            f'<p>User : @{request.user.pseudo}</p>'
            f'<p>Type : {type_probleme}</p>'
            f'<p>Description : {description}</p>'
        )

        logger.info('reclamation_soumise', {'user_id': str(request.user.id)})
        return Response({'message': 'Reclamation envoyee. Nous vous repondrons sous 24h.'})


class StatsUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from cotisations.models import Cotisation, Participation
        from quickpay.models import QuickPay

        nb_crees = Cotisation.objects.filter(createur=user, supprime=False).count()
        nb_completes = Cotisation.objects.filter(createur=user, statut='complete').count()
        nb_participations = Participation.objects.filter(participant=user, statut='paye').count()
        nb_qp_envoyes = QuickPay.objects.filter(createur=user).count()
        nb_qp_recus = QuickPay.objects.filter(numero_payeur=user.telephone, statut='paye').count()

        return Response({
            'cotisations_creees': nb_crees,
            'cotisations_completes': nb_completes,
            'participations': nb_participations,
            'note_moyenne': float(user.note_moyenne),
            'nb_notes': user.nb_notes_recues,
            'quickpay_envoyes': nb_qp_envoyes,
            'quickpay_recus': nb_qp_recus,
            'nb_parrainages': user.nb_parrainages_actifs,
            'niveau': user.niveau,
        })


class StatsFinancieresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from paiements.models import Transaction
        periode = request.query_params.get('periode', '30')
        from django.utils import timezone
        depuis = timezone.now() - timezone.timedelta(days=int(periode))

        transactions = Transaction.objects.filter(
            user=request.user,
            date_creation__gte=depuis,
            statut='complete'
        )

        total_envoye = sum(
            t.montant for t in transactions if t.type_transaction == 'payin'
        )
        total_recu = sum(
            t.montant for t in transactions if t.type_transaction == 'payout'
        )
        total_frais = sum(t.frais_kotizo for t in transactions)

        return Response({
            'periode_jours': int(periode),
            'total_envoye': float(total_envoye),
            'total_recu': float(total_recu),
            'total_frais': float(total_frais),
            'nb_transactions': transactions.count(),
        })


class ParrainageStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from cotisations.models import Cotisation

        filleuls = User.objects.filter(parrain=user, is_active=True)
        filleuls_actifs_verifie = sum(
            1 for f in filleuls
            if Cotisation.objects.filter(createur=f, statut='complete').count() >= 3
        )
        filleuls_actifs_business = sum(
            1 for f in filleuls
            if Cotisation.objects.filter(createur=f, statut='complete').count() >= 3
        )

        return Response({
            'code_parrainage': user.code_parrainage,
            'total_filleuls': filleuls.count(),
            'nb_parrainages_actifs': user.nb_parrainages_actifs,
            'filleuls_actifs_verifie': filleuls_actifs_verifie,
            'filleuls_actifs_business': filleuls_actifs_business,
            'seuil_ambassadeur_verifie': {
                'parrainages': {'objectif': 50, 'actuel': user.nb_parrainages_actifs},
                'filleuls': {'objectif': 25, 'actuel': filleuls_actifs_verifie},
            },
            'seuil_ambassadeur_business': {
                'parrainages': {'objectif': 100, 'actuel': user.nb_parrainages_actifs},
                'filleuls': {'objectif': 50, 'actuel': filleuls_actifs_business},
            },
        })


class SupprimerCompteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        password = request.data.get('password', '')

        if not user.check_password(password):
            return Response({'error': 'Mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        from cotisations.models import Cotisation
        cotisations_actives = Cotisation.objects.filter(
            createur=user, statut='active', supprime=False
        )
        if cotisations_actives.exists():
            return Response(
                {'error': 'Impossible : vous avez des cotisations actives.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        derniere = Cotisation.objects.filter(
            createur=user
        ).order_by('-date_expiration').first()

        if derniere:
            delai = derniere.date_expiration + timezone.timedelta(days=7)
            if timezone.now() < delai:
                return Response(
                    {'error': f'Suppression possible apres {delai.strftime("%d/%m/%Y")}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        user.is_active = False
        user.statut = 'supprime'
        user.date_suppression = timezone.now()
        user.save()

        logger.info('compte_supprime', {'user_id': str(user.id)})
        return Response({'message': 'Compte supprime avec succes.'})
