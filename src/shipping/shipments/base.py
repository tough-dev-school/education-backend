from abc import ABCMeta, abstractmethod

from django.core.exceptions import ImproperlyConfigured

from app.tasks import send_mail


class BaseShipment(metaclass=ABCMeta):
    template_id = None

    def __init__(self, user, stuff):
        self.stuff_to_ship = stuff
        self.user = user

    def __call__(self):
        self.ship()

    @abstractmethod
    def ship(self):
        raise NotImplementedError()

    def send_email(self):
        """Send email, convinience method for subclasses

        The mail is not sent by default, you have to call it manualy!
        """
        return send_mail.delay(
            to=self.user.email,
            template_id=self.get_template_id(),
            ctx=self.get_template_context(),
        )

    def get_template_id(self):
        if hasattr(self.stuff_to_ship, 'get_template_id'):  # per-item template_id
            template_id = self.stuff_to_ship.get_template_id()

            if template_id is not None:
                return template_id

        if self.template_id is None:  # default template_id
            raise ImproperlyConfigured('Please send template_id prop before sending mail')

        return self.template_id

    def get_template_context(self):
        """Template context, empty by default"""
        return dict()
