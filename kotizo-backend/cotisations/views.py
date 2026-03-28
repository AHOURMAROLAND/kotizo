from rest_framework.views import APIView
from rest_framework.response import Response

class CotisationListView(APIView):
    def get(self, request):
        return Response({'message': 'Cotisations endpoint'})
