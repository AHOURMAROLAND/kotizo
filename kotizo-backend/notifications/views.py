from rest_framework.views import APIView
from rest_framework.response import Response

class NotificationListView(APIView):
    def get(self, request):
        return Response({'message': 'Notifications endpoint'})
