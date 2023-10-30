from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from apps.mailing.tasks import send_mail
from apps.users.models import User
from core.models import models
from core.models import TimestampedModel


class EmailLeadCampaignQuerySet(models.QuerySet):
    def with_lead_count(self) -> "EmailLeadCampaignQuerySet":
        return self.annotate(lead_count=Count("leadcampaignlogentry"))


EmailLeadCampaignManager = models.Manager.from_queryset(EmailLeadCampaignQuerySet)


class EmailLeadMagnetCampaign(TimestampedModel):
    objects = EmailLeadCampaignManager()

    name = models.CharField(_("Name"), max_length=32)
    slug = models.SlugField(unique=True)

    template_id = models.CharField(_("Letter template id"), max_length=255, help_text=_("Will be sent upon amocrm_lead registration"))

    success_message = models.CharField(_("Success Message"), max_length=255, help_text=_("Will be shown under tilda form"))

    class Meta:
        verbose_name = _("Email Lead Magnet Campaign")
        verbose_name_plural = _("Email Lead Magnet Campaigns")

    def execute(self, user: User) -> None:
        send_mail.delay(
            to=user.email,
            template_id=self.template_id,
            ctx={
                "campaign_name": self.name,
                "firstname": user.first_name,
                "lastname": user.last_name,
            },
            disable_antispam=True,
        )


class LeadCampaignLogEntry(TimestampedModel):
    campaign = models.ForeignKey(EmailLeadMagnetCampaign, on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
