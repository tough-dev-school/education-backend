from typing import TYPE_CHECKING

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import functions as fn, Count
from django.db.transaction import atomic

if TYPE_CHECKING:
    from users.models import User

USER_RELATIONS = {
    'passwordlessauthtoken_set': 'user',
    'answer_set': 'author',
    'leadcampaignlogentry_set': 'user',
    'order_set': 'user',
    'created_gifts': 'giver',
    'answeraccesslogentry_set': 'user',  # UC answer, user
    'answercrosscheck_set': 'checker',  # UC answer, checker
    'study_set': 'student'  # UC student, course
}
USER_PROPERTIES = (
    'first_name',
    'last_name',
    'first_name_en',
    'last_name_en',
    'subscribed',
    'gender'
)


class Command(BaseCommand):
    help = 'merge active user accounts with same email into one latest joined'

    def users_query(self):
        """
        active users, who has email, annotated with lowercased email version
        """
        UserClass = apps.get_model('users.User')  # noqa
        return UserClass.objects\
            .filter(is_active=True)\
            .filter(email__contains='@')\
            .annotate(email_lower=fn.Lower('email'))

    def duplicate_email_query(self):
        """
        amount of users by email (case insensitive),
        if there are more than 1
        """
        q = self.users_query()
        return q.values('email_lower') \
            .annotate(count=Count('email_lower')) \
            .filter(count__gt=1)

    def merge_user(self, source: 'User', target: 'User'):
        """Merge source user into target user, considering all relations.
        Some relations, which have unique constraint on user,
        might be duplicated as result of merge. Such relations are left untouched with source user.
        """
        for prop_name in USER_PROPERTIES:
            # update target property only if target is empty/false,
            # and source is not empty/true
            target_prop = getattr(target, prop_name)
            source_prop = getattr(source, prop_name)
            if not target_prop and source_prop:
                self.stdout.write(f'updating "{target}".{prop_name} from "{source}"')
                setattr(target, prop_name, source_prop)

        # Merging user relations
        for relation_attr, relation_name in USER_RELATIONS.items():
            relation = getattr(source, relation_attr)
            for i in relation.all():
                self.stdout.write(f'moving {i} from "{source}".{relation_attr} to "{target}"')
                setattr(i, relation_name, target)

                with atomic():
                    # we already run whole `handle` method inside transaction,
                    # so we need another transaction layer to handle integrity errors with grace
                    # https://docs.djangoproject.com/en/3.2/topics/db/transactions/
                    try:
                        i.save()
                    except IntegrityError as e:
                        # There are some user relations, that have unique constraint, involving user reference.
                        # So a situation is possible, when relation that being moved,
                        # already has a duplicate in target relation set
                        # Current tactic is to ignore such cases and to leave the relation in source
                        self.stdout.write(f'integrity error on saving "{i}": {e}')

        # We will lowercase username as well as email,
        # but for username, we need to keep it unique.
        # So we replace username of deprecated users (which is their email) with their uuid
        source.username = source.uuid
        source.is_active = False  # disable user instead of physically delete it
        source.save()
        self.stdout.write(f'finished merging "{source}" into "{target}"')

    def handle_single_email(self, email):
        """Merges all users with same email (case insensitive),
        into last registered user, in order of join date.
        """
        self.stdout.write(f'working on "{email.lower()}"')
        same_users = self.users_query().filter(email__iexact=email).order_by('-date_joined').all()
        target_user, source_user_list = same_users[0], same_users[1:]

        for source_user in source_user_list:
            self.merge_user(source_user, target_user)

        target_user.username = target_user.username.lower()
        target_user.email = target_user.email.lower()
        target_user.save()
        self.stdout.write(f'finish merging {email}')

    @atomic
    def handle(self, *args, **options):
        duplicate_emails = self.duplicate_email_query()

        for record in duplicate_emails:
            self.handle_single_email(record['email_lower'])

        self.stdout.write(f'{len(duplicate_emails)} emails are handled!')
