from django.db.models import Count, Q, QuerySet
from django.db.models.query_utils import FilteredRelation
from django.utils.translation import gettext_lazy as _
from tree_queries.models import  TreeQuerySet


class AnswerQuerySet(TreeQuerySet):
    def for_viewset(self) -> QuerySet['Answer']:
        return self.with_tree_fields().select_related('author', 'question')

    def accessed_by(self, user) -> QuerySet['Answer']:
        return self.with_tree_fields().annotate(
            access_log_entries_for_this_user=FilteredRelation('answeraccesslogentry', condition=Q(answeraccesslogentry__user=user)),
        ).filter(Q(author=user) | Q(access_log_entries_for_this_user__user=user))

    def for_user(self, user):
        """Return all child answers of any answers that have ever been accessed by given user"""
        accessed_answers = self.accessed_by(user)

        roots_of_accessed_answers = [str(answer.tree_path[0]) for answer in accessed_answers.iterator()]

        if len(roots_of_accessed_answers) > 0:
            return self.with_tree_fields().extra(where=[f'tree_path[1] in ({",".join(roots_of_accessed_answers)})'])
        else:
            return self.none()

    def with_crosscheck_count(self):
        return self.annotate(crosscheck_count=Count('answercrosscheck'))

    def root_only(self):
        return self.filter(parent__isnull=True)

