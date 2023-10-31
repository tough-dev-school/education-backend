from drf_recaptcha.fields import ReCaptchaV3Field

from core import validators


class LeadValidator(validators.Validator):
    name = validators.CharField(required=False)
    email = validators.EmailField(required=True)
    recaptcha = ReCaptchaV3Field(
        action="lead_magnet",
    )

    class Meta:
        fields = [
            "name",
            "email",
        ]

    def validate(self, attrs: dict) -> dict:
        attrs.pop("recaptcha")
        return attrs
