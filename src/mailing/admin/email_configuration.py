from app.admin import StackedInline
from mailing.models import EmailConfiguration


class EmailConfigurationAdmin(StackedInline):
    model = EmailConfiguration

    fields = [
        "backend",
        "from_email",
        "reply_to",
        "backend_options",
    ]
