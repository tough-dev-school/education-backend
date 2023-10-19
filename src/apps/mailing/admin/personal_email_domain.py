from apps.mailing.models import PersonalEmailDomain
from core.admin import admin
from core.admin import ModelAdmin


@admin.register(PersonalEmailDomain)
class PersonalEmailDomainAdmin(ModelAdmin):
    list_display = ("name",)
