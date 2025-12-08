from apps.users.models import User
from apps.users.services import UserCreator
from core.test import factory


@factory.register
def user(self: factory.FixtureFactory) -> User:
    user_creator = UserCreator(
        name=self.faker.name(),
        email=self.faker.email(),
    )

    return user_creator.create()  # directly calling internal method to save a query
