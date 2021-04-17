class MailchimpException(BaseException):
    """Base mailchimp exception"""


class MailchimpHTTPException(MailchimpException):
    pass


class MailchimpWrongResponse(MailchimpHTTPException):
    pass


class MailchimpNotFound(MailchimpHTTPException):
    pass


class MailchimpSubscriptionFailed(MailchimpException):
    pass
