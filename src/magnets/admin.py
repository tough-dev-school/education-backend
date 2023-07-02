from rest_framework.request import Request

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from app.admin import admin
from app.admin import ModelAdmin
from magnets.models import EmailLeadMagnetCampaign


@admin.register(EmailLeadMagnetCampaign)
class EmailLeadMagnetCampaignAdmin(ModelAdmin):
    fields = [
        "name",
        "slug",
        "template_id",
        "success_message",
    ]

    list_display = [
        "name",
        "slug",
        "lead_count",
    ]

    prepopulated_fields = {
        "slug": ["name"],
    }

    def get_queryset(self, request: Request) -> QuerySet[EmailLeadMagnetCampaign]:  # type: ignore
        return super().get_queryset(request).with_lead_count()  # type: ignore

    @admin.display(description=_("Lead count"), ordering="lead_count")
    def lead_count(self, obj: EmailLeadMagnetCampaign | None = None) -> str:
        return obj.lead_count if obj and hasattr(obj, "lead_count") and obj.lead_count else "—"
