from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from core.logger import logger
from .models import ConversationIA, MessageIA, TicketSupport
from .serializers import ConversationIASerializer, MessageIASerializer, TicketSupportSerializer
from .utils import detecter_injection, appeler_gemini, construire_contexte_user

LIMITE_MESSAGE = 1000


class ConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversation = ConversationIA.objects.filter(
            user=request.user
        ).first()
        if not conversation:
            return Response({'messages': []})
        return Response(ConversationIASerializer(conversation).data)

    def post(self, request):
        message_user = request.data.get('message', '').strip()
        image_url = request.data.get('image_url', '')

        if not message_user:
            return Response({'error': 'Message vide'}, status=status.HTTP_400_BAD_REQUEST)

        if len(message_user) > LIMITE_MESSAGE:
            return Response(
                {'error': f'Message trop long - maximum {LIMITE_MESSAGE} caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if detecter_injection(message_user):
            logger.warning(f'Injection IA detectee', user_id=str(request.user.id))
            return Response(
                {'error': 'Message non autorise'},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation, _ = ConversationIA.objects.get_or_create(user=request.user)

        MessageIA.objects.create(
            conversation=conversation,
            role='user',
            contenu=message_user,
            image_url=image_url,
        )

        historique = list(
            conversation.messages.order_by('date_creation').values('role', 'contenu')
        )

        contexte_user = construire_contexte_user(request.user)
        reponse_ia = appeler_gemini(historique, contexte_user)

        message_ia = MessageIA.objects.create(
            conversation=conversation,
            role='assistant',
            contenu=reponse_ia,
        )

        conversation.nb_messages += 2
        conversation.save(update_fields=['nb_messages', 'date_derniere_activite'])

        logger.ia('Reponse generee', user_id=str(request.user.id), action_ia='reponse')

        return Response(MessageIASerializer(message_ia).data)


class EffacerConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        ConversationIA.objects.filter(user=request.user).delete()
        return Response({'message': 'Conversation effacee'})


class TicketSupportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = TicketSupport.objects.filter(user=request.user)
        return Response(TicketSupportSerializer(tickets, many=True).data)

    def post(self, request):
        serializer = TicketSupportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ticket = serializer.save(user=request.user)
        logger.info(f'Ticket support cree', user_id=str(request.user.id))
        return Response(TicketSupportSerializer(ticket).data, status=status.HTTP_201_CREATED)


class TicketDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        try:
            ticket = TicketSupport.objects.get(id=ticket_id, user=request.user)
            return Response(TicketSupportSerializer(ticket).data)
        except TicketSupport.DoesNotExist:
            return Response({'error': 'Ticket introuvable'}, status=status.HTTP_404_NOT_FOUND)