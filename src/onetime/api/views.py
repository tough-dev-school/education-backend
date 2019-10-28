from django.shortcuts import get_object_or_404, redirect

from app.views import AnonymousAPIView
from onetime.models import Token


class TokenDownloadView(AnonymousAPIView):
    def get(self, request, token):
        queryset = Token.objects.active()
        token = get_object_or_404(queryset, token=token)
        print(token, queryset)
        print(token.expires)

        return redirect(token.download())
