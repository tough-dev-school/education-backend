from apps.mailing.models import EmailConfiguration
from core.admin import StackedInline


class EmailConfigurationAdmin(StackedInline):
    model = EmailConfiguration

    fields = [
        "backend",
        "from_email",
        "reply_to",
        "backend_options",
    ]
