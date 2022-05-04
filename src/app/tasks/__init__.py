from app.tasks.dashamail import subscribe_to_dashamail
from app.tasks.mail import send_mail
from app.tasks.tg import send_happiness_message
from app.tasks.zoomus import invite_to_zoomus

__all__ = [
    'invite_to_zoomus',
    'send_happiness_message',
    'send_mail',
    'subscribe_to_dashamail',
]
