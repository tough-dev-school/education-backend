from app.admin import StackedInline
from mailing.models import EmailConfiguration


class EmailConfigurationAdmin(StackedInline):
    model = EmailConfiguration

    fields = [
        "backend",
        "from_email",
        "backend_options",
    ]
