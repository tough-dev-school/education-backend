from core.admin import admin
from core.admin import ModelAdmin
from apps.mailing.models import PersonalEmailDomain


@admin.register(PersonalEmailDomain)
class PersonalEmailDomainAdmin(ModelAdmin):
    list_display = ("name",)
