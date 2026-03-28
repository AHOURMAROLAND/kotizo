import random
import string
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from core.logger import KotizoLogger
from core.email_router import envoyer_email
from core.whatsapp import envoyer_message
from users.models import User, SessionDevice
from users.serializers import InscriptionSerializer, ConnexionSerializer

logger = KotizoLogger('auth')


def generer_otp():
    return ''.join(random.choices(string.digits, k=6))


def generer_token_wa():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


class InscriptionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        otp = generer_otp()
        token_wa = generer_token_wa()

        cache.set(f'inscription_email_{user.email}', otp, timeout=120)
        cache.set(f'inscription_wa_{user.telephone}', token_wa, timeout=120)

        tentatives_key = f'inscription_tentatives_{user.telephone}'
        tentatives = cache.get(tentatives_key, 0)
        cache.set(tentatives_key, tentatives + 1, timeout=86400)

        try:
            envoyer_email(
                user.email,
                'Code de verification Kotizo',
                f'<h2>Votre code : <strong>{otp}</strong></h2>'
                f'<p>Ce code expire dans 2 minutes.</p>'
            )
        except Exception as e:
            logger.error('email_otp_echec', {'erreur': str(e)})

        logger.info('inscription_initiee', {'user_id': str(user.id)})

        return Response({
            'message': 'Compte cree. Veuillez verifier votre identite.',
            'user_id': str(user.id),
            'token_wa': f'KOTIZO-VERIFY-{token_wa}',
            'canal': 'email_ou_whatsapp'
        }, status=status.HTTP_201_CREATED)


class VerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower()
        otp = request.data.get('otp', '')

        otp_stocke = cache.get(f'inscription_email_{email}')

        if not otp_stocke:
            return Response(
                {'error': 'Code expire. Recommencez l inscription.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp != otp_stocke:
            return Response(
                {'error': 'Code incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            user.email_verifie = True
            user.is_active = True
            user.save()
            cache.delete(f'inscription_email_{email}')

            refresh = RefreshToken.for_user(user)
            logger.info('email_verifie', {'user_id': str(user.id)})

            return Response({
                'message': 'Email verifie avec succes.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)


class VerificationWhatsAppView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        telephone = request.data.get('telephone', '')
        token = request.data.get('token', '').replace('KOTIZO-VERIFY-', '')

        token_stocke = cache.get(f'inscription_wa_{telephone}')

        if not token_stocke:
            return Response(
                {'error': 'Token expire. Recommencez l inscription.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if token != token_stocke:
            return Response({'error': 'Token invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(telephone=telephone)
            user.whatsapp_verifie = True
            user.is_active = True
            user.save()
            cache.delete(f'inscription_wa_{telephone}')

            refresh = RefreshToken.for_user(user)
            logger.info('whatsapp_verifie', {'user_id': str(user.id)})

            return Response({
                'message': 'WhatsApp verifie avec succes.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)


class ConnexionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConnexionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']

        if user.identite_verifiee:
            numero_cni = request.data.get('numero_cni', '')
            if not numero_cni:
                return Response(
                    {'require_cni': True, 'message': 'Saisie CNI requise.'},
                    status=status.HTTP_200_OK
                )
            import hashlib
            hash_saisi = hashlib.sha256(numero_cni.strip().encode()).hexdigest()
            if hash_saisi != user.numero_cni_hash:
                return Response(
                    {'error': 'Numero CNI incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        device_id = request.data.get('device_id', 'unknown')
        device_name = request.data.get('device_name', 'Appareil inconnu')

        sessions_actives = SessionDevice.objects.filter(user=user, is_active=True)
        nouvel_appareil = not sessions_actives.filter(device_id=device_id).exists()

        sessions_actives.update(is_active=False)
        SessionDevice.objects.create(
            user=user,
            device_id=device_id,
            device_name=device_name,
            ip_address=request.META.get('REMOTE_ADDR'),
            is_active=True
        )

        if nouvel_appareil and sessions_actives.exists():
            msg = (
                f"Nouvelle connexion detectee sur votre compte Kotizo\n"
                f"Appareil : {device_name}\n"
                f"Si ce n'est pas vous, signalez-le dans l'app."
            )
            try:
                envoyer_message(user.whatsapp_numero or user.telephone, msg)
                envoyer_email(user.email, 'Nouvelle connexion Kotizo', f'<p>{msg}</p>')
            except Exception:
                pass

        refresh = RefreshToken.for_user(user)
        logger.info('connexion_reussie', {'user_id': str(user.id)})

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'pseudo': user.pseudo,
                'niveau': user.niveau,
                'theme': user.theme_preference,
                'mode': user.mode_preference,
                'identite_verifiee': user.identite_verifiee,
                'nouvel_appareil': nouvel_appareil,
            }
        })


class DeconnexionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            SessionDevice.objects.filter(
                user=request.user, is_active=True
            ).update(is_active=False)
            return Response({'message': 'Deconnexion reussie.'})
        except Exception:
            return Response({'error': 'Token invalide.'}, status=status.HTTP_400_BAD_REQUEST)


class MotDePasseOublieView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower()
        try:
            user = User.objects.get(email=email)
            token = generer_token_wa()
            cache.set(f'reset_mdp_{email}', token, timeout=1800)
            lien = f"kotizo.app/reset-password/{token}"
            envoyer_email(
                email,
                'Reinitialisation mot de passe Kotizo',
                f'<p>Cliquez ici pour reinitialiser : <a href="{lien}">{lien}</a></p>'
                f'<p>Ce lien expire dans 30 minutes.</p>'
            )
        except User.DoesNotExist:
            pass
        return Response({'message': 'Si cet email existe, un lien a ete envoye.'})


class ChangerMotDePasseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ancien = request.data.get('ancien_password', '')
        nouveau = request.data.get('nouveau_password', '')
        if not request.user.check_password(ancien):
            return Response({'error': 'Ancien mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(nouveau) < 8:
            return Response({'error': 'Minimum 8 caracteres.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(nouveau)
        request.user.save()
        return Response({'message': 'Mot de passe modifie.'})


class ConfirmerActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get('password', '')
        if not request.user.check_password(password):
            return Response({'error': 'Mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'confirme': True})


class VerifierCNIConnexionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import hashlib
        numero = request.data.get('numero_cni', '')
        hash_saisi = hashlib.sha256(numero.strip().encode()).hexdigest()
        if hash_saisi == request.user.numero_cni_hash:
            return Response({'valide': True})
        return Response({'error': 'Numero CNI incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
