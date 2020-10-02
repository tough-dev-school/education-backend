from app.admin import ModelAdmin, admin
from magnets.models import EmailLeadMagnetCampaign


@admin.register(EmailLeadMagnetCampaign)
class EmailLeadMagnetCampaignAdmin(ModelAdmin):
    fields = [
        'name',
        'slug',
        'template_id',
    ]

    prepopulated_fields = {
        'slug': ['name'],
    }
