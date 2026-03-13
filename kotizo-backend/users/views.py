from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.logger import logger
from .serializers import (
    InscriptionSerializer, UserSerializer,
    UserProfilSerializer, VerificationIdentiteSerializer
)

User = get_user_model()


class InscriptionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        logger.auth('Nouvel utilisateur inscrit', user_id=str(user.id))

        from .tasks import envoyer_email_verification
        envoyer_email_verification.delay(str(user.id))

        return Response({
            'message': 'Compte cree. Verifiez votre email pour activer votre compte.',
            'email': user.email,
        }, status=status.HTTP_201_CREATED)


class VerifierEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            user = User.objects.get(token_verification_email=token, email_verifie=False)
        except User.DoesNotExist:
            return Response({'error': 'Lien invalide ou deja utilise'}, status=status.HTTP_400_BAD_REQUEST)

        user.email_verifie = True
        user.token_verification_email = ''
        user.save()
        logger.auth('Email verifie', user_id=str(user.id))

        return Response({'message': 'Email verifie avec succes. Vous pouvez vous connecter.'})


class ConnexionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Identifiants incorrects'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            logger.auth('Tentative connexion echouee', ip=request.META.get('REMOTE_ADDR'))
            return Response({'error': 'Identifiants incorrects'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.email_verifie:
            return Response({'error': 'Veuillez verifier votre email avant de vous connecter'}, status=status.HTTP_403_FORBIDDEN)

        if not user.is_active:
            return Response({'error': 'Compte suspendu. Contactez le support.'}, status=status.HTTP_403_FORBIDDEN)

        user.derniere_connexion_app = timezone.now()
        user.save(update_fields=['derniere_connexion_app'])

        refresh = RefreshToken.for_user(user)
        logger.auth('Connexion reussie', user_id=str(user.id))

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })


class DeconnexionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass
        return Response({'message': 'Deconnecte avec succes'})


class MoiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserProfilSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class FCMTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        fcm_token = request.data.get('fcm_token', '')
        device_id = request.data.get('device_id', '')
        request.user.fcm_token = fcm_token
        request.user.device_id = device_id
        request.user.save(update_fields=['fcm_token', 'device_id'])
        return Response({'message': 'Token FCM mis a jour'})