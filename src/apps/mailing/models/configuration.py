from django.utils.translation import gettext_lazy as _

from core.models import models
from core.models import TimestampedModel


class EmailConfiguration(TimestampedModel):
    """Configuration is the low-level email backend settings, e.g. email backend class, `mail_from`, or raw backend kwargs"""

    class BACKEND(models.TextChoices):
        UNSET = "", _("Unset")
        POSTMARK = "anymail.backends.postmark.EmailBackend", _("Postmark")

    backend = models.CharField(max_length=256, choices=BACKEND.choices, default=BACKEND.UNSET)
    course = models.OneToOneField("products.Course", related_name="email_configuration", on_delete=models.CASCADE)
    from_email = models.CharField(_("Email sender"), max_length=256, help_text=_("E.g. Fedor Borshev &lt;fedor@borshev.com&gt;. MUST configure postmark!"))
    reply_to = models.CharField(_("Reply-to header"), max_length=256, help_text=_("E.g. Fedor Borshev &lt;fedor@borshev.com&gt;"))

    backend_options = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("Email configuration")
        verbose_name_plural = _("Email configurations")

    def __str__(self) -> str:
        if self.course is not None:
            return str(self.course)

        return super().__str__()  # type: ignore
