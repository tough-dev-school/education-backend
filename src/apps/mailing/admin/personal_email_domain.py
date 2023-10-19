from app.admin import admin
from app.admin import ModelAdmin
from apps.mailing.models import PersonalEmailDomain


@admin.register(PersonalEmailDomain)
class PersonalEmailDomainAdmin(ModelAdmin):
    list_display = ("name",)
