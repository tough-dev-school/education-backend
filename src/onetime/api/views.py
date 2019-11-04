from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View

from onetime.models import Token


class TokenDownloadView(View):
    def get(self, request, token):
        queryset = Token.objects.active()
        token = get_object_or_404(queryset, token=token)

        return redirect(token.download())
