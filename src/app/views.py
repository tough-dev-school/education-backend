from django.views.generic import RedirectView
from rest_framework import permissions
from rest_framework.views import APIView


class AnonymousAPIView(APIView):
    permission_classes = [permissions.AllowAny]


class HomePageView(RedirectView):
    url = '/admin/'
