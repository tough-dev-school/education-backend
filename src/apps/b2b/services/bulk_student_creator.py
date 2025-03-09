from dataclasses import dataclass

from apps.b2b.models import Deal, Student
from apps.users.services import UserCreator
from core.services import BaseService


@dataclass
class BulkStudentCreator(BaseService):
    user_input: str
    deal: Deal

    def act(self) -> int:
        emails = self.get_emails(self.user_input)
        self.create_students(emails)

        return len(emails)

    @staticmethod
    def get_emails(user_input: str) -> list[str]:
        user_input = user_input.replace(",", "\n").replace(";", "\n")
        emails = [email.strip().strip(".") for email in user_input.split("\n") if "@" in email]

        return emails

    def create_students(self, emails: list[str]) -> None:
        for email in emails:
            user = UserCreator(email=email)()
            Student.objects.get_or_create(deal=self.deal, user=user)
