from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import functions as fn
from django.db.transaction import atomic

from a12n.models import PasswordlessAuthToken
from homework.models import Answer, AnswerAccessLogEntry, AnswerCrossCheck
from magnets.models import LeadCampaignLogEntry
from orders.models import Order
from studying.models import Study
from users.models import User


class Command(BaseCommand):
    help = 'merge active user accounts with same email into one latest joined'

    def merge_user(self, source: User, target: User):
        """Merge source user into target user, considering all relations.
        Some relations, which have unique constraint on user,
        might be duplicated as result of merge. Such relations are left untouched with source user.
        """
        self.stdout.write(f'merging "{source}" into "{target}"')

        # merging user properties
        target.first_name = target.first_name or source.first_name
        target.last_name = target.last_name or source.last_name
        target.first_name_en = target.first_name_en or source.first_name_en
        target.last_name_en = target.last_name_en or source.last_name_en
        target.subscribed = target.subscribed or source.subscribed
        target.gender = target.gender or source.gender

        # Merging safe user relations
        PasswordlessAuthToken.objects.filter(user=source).update(user=target)
        Answer.objects.filter(author=source).update(author=target)
        LeadCampaignLogEntry.objects.filter(user=source).update(user=target)
        Order.objects.filter(user=source).update(user=target)
        Order.objects.filter(giver=source).update(giver=target)

        # Merging possibly overlapping relations, leaving as is on collision
        # try:
        #     with atomic():
        #         AnswerAccessLogEntry.objects.filter(user=source).update(user=target)  # UC answer user
        # except IntegrityError as e:
        #     self.stdout.write(f'integrity error on updating "{source}" AnswerAccessLogEntry: {e}')
        #
        # try:
        #     with atomic():
        #         AnswerCrossCheck.objects.filter(checker=source).update(checker=target)  # UC answer checker
        # except IntegrityError as e:
        #     self.stdout.write(f'integrity error on updating "{source}" AnswerCrossCheck: {e}')
        #
        # try:
        #     with atomic():
        #         Study.objects.filter(student=source).update(student=target)  # UC student course
        # except IntegrityError as e:
        #     self.stdout.write(f'integrity error on updating "{source}" Study: {e}')

        # We will lowercase username as well as email,
        # but for username, we need to keep it unique.
        # So we replace username of deprecated users (which is their email) with their uuid
        source.username = source.uuid
        source.is_active = False  # disable user instead of physically delete it
        source.save()
        self.stdout.write(f'merged "{source}" into "{target}"')

    def handle_single_email(self, email):
        """Merges all users with sa me email (case insensitive),
        into last registered user, in order of join date.
        """
        self.stdout.write(f'handling {email}')
        same_users = User.objects.filter(is_active=True).filter(email__iexact=email).order_by('-date_joined')
        target, sources = same_users[0], same_users[1:]

        for source in sources:
            self.merge_user(source, target)

        target.username = target.username.lower()
        target.email = target.email.lower()
        target.save()
        self.stdout.write(f'handled {email}')

    @atomic
    def handle(self, *args, **options):
        active_users_emails = User.objects\
            .filter(is_active=True)\
            .annotate(lower_email=fn.Lower('email'))\
            .values('lower_email')\
            .distinct()

        for row in active_users_emails:
            self.handle_single_email(row['lower_email'])
