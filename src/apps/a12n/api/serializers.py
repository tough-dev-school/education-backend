from dj_rest_auth.serializers import PasswordResetSerializer as DjRestAuthPasswordResetSerializer

from apps.a12n.api.forms import EspTemplatePasswordResetForm


class PasswordResetSerializer(DjRestAuthPasswordResetSerializer):
    password_reset_form_class = EspTemplatePasswordResetForm
