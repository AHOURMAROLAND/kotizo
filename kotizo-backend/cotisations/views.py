from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from core.logger import logger
from .models import Cotisation, Participation, Signalement
from .serializers import (
    CotisationCreateSerializer, CotisationSerializer,
    ParticipationSerializer, SignalementSerializer
)
from .utils import generer_slug, detecter_operateur


class CotisationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cotisations = Cotisation.objects.filter(createur=request.user)
        serializer = CotisationSerializer(cotisations, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user

        if not user.email_verifie:
            return Response({'error': 'Email non verifie'}, status=status.HTTP_403_FORBIDDEN)

        limite = user.get_limite_cotisations()
        if limite and user.cotisations_creees_aujourd_hui >= limite:
            return Response(
                {'error': f'Limite de {limite} cotisations par jour atteinte'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = CotisationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        operateur = detecter_operateur(serializer.validated_data['numero_receveur'])
        cotisation = serializer.save(
            createur=user,
            slug=generer_slug(),
            operateur_receveur=operateur,
        )

        user.cotisations_creees_aujourd_hui += 1
        user.save(update_fields=['cotisations_creees_aujourd_hui'])

        logger.cotisation('Cotisation creee', user_id=str(user.id), cotisation_id=str(cotisation.id))

        return Response(CotisationSerializer(cotisation).data, status=status.HTTP_201_CREATED)


class CotisationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        cotisation = get_object_or_404(Cotisation, slug=slug)
        serializer = CotisationSerializer(cotisation)
        data = serializer.data

        participation = Participation.objects.filter(
            cotisation=cotisation,
            participant=request.user
        ).first()
        data['ma_participation'] = ParticipationSerializer(participation).data if participation else None
        data['est_createur'] = cotisation.createur == request.user

        return Response(data)

    def delete(self, request, slug):
        cotisation = get_object_or_404(Cotisation, slug=slug, createur=request.user)
        if cotisation.participants_payes > 0:
            return Response(
                {'error': 'Impossible de supprimer une cotisation avec des paiements'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cotisation.statut = 'annulee'
        cotisation.save()
        logger.cotisation('Cotisation annulee', user_id=str(request.user.id), cotisation_id=str(cotisation.id))
        return Response(status=status.HTTP_204_NO_CONTENT)


class RejoindreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        cotisation = get_object_or_404(Cotisation, slug=slug, statut='active')

        if cotisation.createur == request.user:
            return Response({'error': 'Le createur ne peut pas participer a sa propre cotisation'}, status=status.HTTP_400_BAD_REQUEST)

        if cotisation.is_complete():
            return Response({'error': 'Cotisation complete'}, status=status.HTTP_400_BAD_REQUEST)

        if Participation.objects.filter(cotisation=cotisation, participant=request.user).exists():
            return Response({'error': 'Vous participez deja a cette cotisation'}, status=status.HTTP_400_BAD_REQUEST)

        participation = Participation.objects.create(
            cotisation=cotisation,
            participant=request.user,
            montant=cotisation.montant_unitaire,
        )

        logger.cotisation('Participation creee', user_id=str(request.user.id), cotisation_id=str(cotisation.id))

        return Response(ParticipationSerializer(participation).data, status=status.HTTP_201_CREATED)


class ConfirmerRecuView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, participation_id):
        participation = get_object_or_404(
            Participation,
            id=participation_id,
            participant=request.user,
            statut='paye'
        )
        participation.recu_confirme = True
        participation.date_confirmation_recu = timezone.now()
        participation.save()
        return Response({'message': 'Recu confirme'})


class ParticipantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        cotisation = get_object_or_404(Cotisation, slug=slug)
        if cotisation.createur != request.user:
            return Response({'error': 'Acces refuse'}, status=status.HTTP_403_FORBIDDEN)
        participants = cotisation.participations.all()
        return Response(ParticipationSerializer(participants, many=True).data)


class SignalerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        cotisation = get_object_or_404(Cotisation, slug=slug)

        if cotisation.createur == request.user:
            return Response({'error': 'Vous ne pouvez pas signaler votre propre cotisation'}, status=status.HTTP_400_BAD_REQUEST)

        if Signalement.objects.filter(cotisation=cotisation, signaleur=request.user).exists():
            return Response({'error': 'Vous avez deja signale cette cotisation'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SignalementSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        signalement = serializer.save(cotisation=cotisation, signaleur=request.user)
        logger.fraude(f'Signalement cotisation {slug}', user_id=str(request.user.id))

        nb_signalements = cotisation.signalements.count()
        if nb_signalements >= 3:
            cotisation.statut = 'suspendue'
            cotisation.save()
            logger.fraude(f'Cotisation {slug} suspendue - 3 signalements')

        return Response({'message': 'Signalement enregistre'}, status=status.HTTP_201_CREATED)


class MesParticipationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        participations = Participation.objects.filter(
            participant=request.user
        ).select_related('cotisation', 'cotisation__createur')
        return Response(ParticipationSerializer(participations, many=True).data)