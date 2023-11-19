from apps.mailing.models import PersonalEmailDomain
from core.admin import ModelAdmin, admin


@admin.register(PersonalEmailDomain)
class PersonalEmailDomainAdmin(ModelAdmin):
    list_display = ("name",)
