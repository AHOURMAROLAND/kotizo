from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer


class NotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        non_lues = request.query_params.get('non_lues')
        if non_lues:
            notifications = notifications.filter(lue=False)
        return Response(NotificationSerializer(notifications, many=True).data)


class MarquerLueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user
            )
            notification.lue = True
            notification.date_lecture = timezone.now()
            notification.save()
            return Response({'message': 'Notification marquee comme lue'})
        except Notification.DoesNotExist:
            return Response({'error': 'Notification introuvable'}, status=status.HTTP_404_NOT_FOUND)


class MarquerToutesLuesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(
            user=request.user,
            lue=False
        ).update(lue=True, date_lecture=timezone.now())
        return Response({'message': 'Toutes les notifications marquees comme lues'})


class NombreNonLuesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, lue=False).count()
        return Response({'non_lues': count})