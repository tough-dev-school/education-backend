from apps.diplomas.models import DiplomaTemplate
from apps.mailing.models import EmailConfiguration
from core.admin import StackedInline, TabularInline


class DiplomaTemplateAdmin(TabularInline):
    model = DiplomaTemplate
    extra = 0
    list_editable = ()


class EmailConfigurationAdmin(StackedInline):
    model = EmailConfiguration

    fields = [
        "backend",
        "from_email",
        "reply_to",
        "backend_options",
    ]


__all__ = [
    "DiplomaTemplateAdmin",
    "EmailConfigurationAdmin",
]
