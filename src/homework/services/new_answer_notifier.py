from django.db.models import QuerySet

from app.tasks import send_mail
from homework.models import Answer
from users.models import User


class NewAnswerNotifier:
    def __init__(self, answer: Answer):
        self.answer = answer

    def __call__(self):
        for user_to_notify in self.get_users_to_notify().iterator():
            self.send_mail_to_user(user_to_notify)

    def send_mail_to_user(self, user: User):
        send_mail.delay(
            to=user.email,
            template_id='new-answer-notification',
            ctx=self.get_notification_context(user),
            disable_antispam=True,
        )

    def get_users_to_notify(self) -> QuerySet[User]:
        """Get all users that have ever written an answer to the root of the disqussion"""
        authors = self.answer.get_root_answer().descendants(include_self=True).values_list('author', flat=True)

        authors = list(authors)  # have to execute this query cuz django-tree-queries fails to compile it

        return User.objects.filter(pk__in=authors).exclude(pk=self.answer.author_id)

    def get_notification_context(self, user: User) -> dict:
        context = {
            'discussion_name': str(self.answer.question),
            'discussion_url': self.answer.get_absolute_url(),
            'answer_title': str(self.answer),
            'author_name': str(self.answer.author),
        }

        if user == self.answer.get_root_answer().author:
            context['is_root_answer_author'] = '1'
        else:
            context['is_non_root_answer_author'] = '1'

        return context
