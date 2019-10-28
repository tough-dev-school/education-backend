from rest_framework import permissions
from rest_framework.views import APIView


class AnonymousAPIView(APIView):
    permission_classes = [permissions.AllowAny]
