from dataclasses import dataclass


@dataclass
class MailchimpMember:
    email: str
    first_name: str
    last_name: str

    def to_mailchimp(self) -> dict:
        return {
            'email_address': self.email,
            'merge_fields': {
                'FNAME': self.first_name,
                'LNAME': self.last_name,
            },
        }
