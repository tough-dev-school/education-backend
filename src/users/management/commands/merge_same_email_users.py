from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from a12n.models import PasswordlessAuthToken
from homework.models import Answer
from magnets.models import LeadCampaignLogEntry
from orders.models import Order
from users.models import User


class Command(BaseCommand):
    help = 'merge active user accounts with same email into one latest joined'

    def merge_user(self, source: User, target: User):
        """Merge source user into target user, considering all relations.
        Some relations, which have unique constraint on user,
        might be duplicated as result of merge. Such relations are left untouched with source user.
        """
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

        # We will lowercase username as well as email,
        # but for username, we need to keep it unique.
        # So we replace username of deprecated users (which is their email) with their uuid
        source.username = source.uuid
        source.email = source.email.lower()
        source.is_active = False  # disable user instead of physically delete it
        source.save()
        self.stdout.write(f'merged "{source.email}" into "{target.email}"')

    def handle_single_email(self, email):
        """Merges all users with sa me email (case insensitive),
        into last registered user, in order of join date.
        """
        same_users = User.objects.filter(is_active=True).filter(email__iexact=email).order_by('-date_joined')
        target, sources = same_users[0], same_users[1:]

        for source in sources:
            self.merge_user(source, target)

        target.username = target.username.lower()
        target.email = target.email.lower()
        target.save()

    @atomic
    def handle(self, *args, **options):
        for user in User.objects.filter(is_active=True):
            self.handle_single_email(user.email)
        self.stdout.write('DONE!')
