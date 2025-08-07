from dj_rest_auth.serializers import PasswordResetSerializer as DjRestAuthPasswordResetSerializer
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework.fields import BooleanField, CharField
from rest_framework.serializers import Serializer
from rest_framework_jwt.utils import jwt_encode_payload

from apps.a12n.api.forms import EspTemplatePasswordResetForm

EXAMPLE_TOKEN = jwt_encode_payload({"sub": "1234567890", "name": "John Doe", "iat": 1516239022})


class PasswordResetSerializer(DjRestAuthPasswordResetSerializer):
    password_reset_form_class = EspTemplatePasswordResetForm


class OkSerializer(Serializer):
    ok = BooleanField(initial=True, read_only=True)


@extend_schema_serializer(examples=[OpenApiExample(name="default", value={"token": EXAMPLE_TOKEN}, response_only=True)])
class TokenSerializer(Serializer):
    token = CharField(read_only=True)
