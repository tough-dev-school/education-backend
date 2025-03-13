from dataclasses import dataclass
from decimal import Decimal

from django.contrib.admin.models import ADDITION

from apps.b2b.models import Deal, Student
from apps.b2b.utils import assign_existing_orders, create_orders
from apps.users.services import UserCreator
from core.current_user import get_current_user
from core.services import BaseService
from core.tasks.write_admin_log import write_admin_log


@dataclass
class BulkStudentCreator(BaseService):
    user_input: str
    deal: Deal

    def act(self) -> int:
        emails = self.get_emails(self.user_input)
        self.create_students(emails)

        if self.deal.completed is not None or self.deal.shipped_without_payment is not None:
            create_orders(deal=self.deal, single_order_price=Decimal(0))
            assign_existing_orders(deal=self.deal)

        return len(emails)

    @staticmethod
    def get_emails(user_input: str) -> list[str]:
        user_input = user_input.replace(",", "\n").replace(";", "\n")
        emails = [email.strip().strip(".") for email in user_input.split("\n") if "@" in email]

        return emails

    def create_students(self, emails: list[str]) -> None:
        for email in emails:
            user = UserCreator(email=email)()
            student, _ = Student.objects.get_or_create(deal=self.deal, user=user)

            self.write_auditlog_for_student_creation(student)

    @staticmethod
    def write_auditlog_for_student_creation(student: Student) -> None:
        user = get_current_user()
        if user is None:
            raise RuntimeError("Cannot determine user")

        write_admin_log.delay(
            action_flag=ADDITION,
            app="b2b",
            change_message="Student created",
            model="Student",
            object_id=student.id,
            user_id=user.id,
        )
