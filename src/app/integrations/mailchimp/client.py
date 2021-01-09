from app.integrations.mailchimp.http import MailchimpHTTP


class AppMailchimp:
    def __init__(self):
        self.http = MailchimpHTTP()


__all__ = [
    AppMailchimp,
]
