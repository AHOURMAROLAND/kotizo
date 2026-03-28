from rest_framework.views import APIView
from rest_framework.response import Response

class AgentIAListView(APIView):
    def get(self, request):
        return Response({'message': 'Agent IA endpoint'})
