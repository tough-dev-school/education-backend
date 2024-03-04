from django.views.generic import RedirectView
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.models import User


class AuthenticatedRequest(Request):
    user: User


class AnonymousAPIView(APIView):
    permission_classes = [permissions.AllowAny]


class AuthenticatedAPIView(APIView):
    request: AuthenticatedRequest
    permission_classes = [permissions.IsAuthenticated]


class HomePageView(RedirectView):
    url = "/admin/"
