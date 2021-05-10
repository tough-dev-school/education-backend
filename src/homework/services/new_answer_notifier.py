from homework.models import Answer
from users.models import User


class NewAnswerNotifier:
    def __init__(self, answer: Answer):
        self.answer = answer

    def get_users_to_notify(self):
        answer_ancestors = self.answer.ancestors(include_self=False)
        user_ids = list(answer_ancestors.values_list('author', flat=True))  # have to execute this query cuz django-tree-query fails to compile it

        return User.objects.filter(pk__in=user_ids).exclude(pk=self.answer.author_id)

    def get_template_context(self):
        return {
            'discussion_name': str(self.answer.question),
            'discussion_url': self.answer.get_absolute_url(),
            'answer_title': str(self.answer),
        }
