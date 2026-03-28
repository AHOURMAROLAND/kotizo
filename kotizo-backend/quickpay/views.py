from rest_framework.views import APIView
from rest_framework.response import Response

class QuickPayListView(APIView):
    def get(self, request):
        return Response({'message': 'QuickPay endpoint'})
