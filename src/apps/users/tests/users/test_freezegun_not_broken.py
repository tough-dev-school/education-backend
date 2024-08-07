import pytest

from apps.users.models import User

pytestmark = [
    pytest.mark.django_db,
]


@pytest.mark.freeze_time("2022-11-23")
def test_queryset_return_updated_data_while_time_freezed():
    """
    Django-cachalot uses time as a key for cache and does not compatible with `freezegun`.
    Test to be sure that queryset returns updated data == cachalot is disabled.
    More details: https://github.com/noripyt/django-cachalot/issues/126
    """
    created_user = User.objects.create(username="created_username")

    fetched_user = User.objects.get(id=created_user.id)
    fetched_user.update(username="updated_username")

    assert User.objects.get(id=created_user.id).username == "updated_username"
