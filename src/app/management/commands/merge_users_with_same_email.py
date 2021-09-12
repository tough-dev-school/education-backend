from collections import defaultdict
from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Merge users with same email'

    def handle(self, *args, **kwargs):
        data = defaultdict(list)
        user_model = apps.get_model('users.User')
        users = user_model.objects.all()
        for user in users:
            data[user.email.lower()].append(user.pk)
        for email, ids in data.items():
            if len(ids) > 1:
                users = user_model.objects.filter(id__in=ids).order_by('date_joined').all()
                self.stdout.write(f'{users.count()} users with email {email} will be merged..')
                result_user = users[0]
                subscribed = any(u.subscribed for u in users)
                result_user.subscribed = subscribed
                result_user.save()
                for item in users[1:]:
                    item.delete()
                self.stdout.write(self.style.SUCCESS('Done!'))
