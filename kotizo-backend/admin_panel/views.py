from rest_framework.views import APIView
from rest_framework.response import Response

class AdminLogListView(APIView):
    def get(self, request):
        return Response({'message': 'Admin Panel endpoint'})
