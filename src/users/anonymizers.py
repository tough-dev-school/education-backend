from hattori.base import BaseAnonymizer, faker

from users.models import User


class UserAnonimizer(BaseAnonymizer):
    model = User
    attributes = [
        ('first_name', faker.first_name),
        ('last_name', faker.last_name),
        ('email', faker.email),
        ('username', faker.ssn),
    ]

    def run(self, *args, **kwargs):
        result = super().run(*args, **kwargs)

        self.set_simple_password_for_all_remaining_users()

        return result

    def get_query_set(self):
        return User.objects.filter(is_staff=False)

    def set_simple_password_for_all_remaining_users(self):
        print('Setting password «123» to all staff users:', end=' ')  # noqa T001
        updated = []
        for user in User.objects.exclude(pk__in=self.get_query_set().values_list('pk')):
            user.set_password('123')
            user.save()
            updated.append(user.username)

        print(', '.join(updated)) # noqa T001
