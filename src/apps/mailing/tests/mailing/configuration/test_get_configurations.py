import pytest

from apps.mailing.configuration import get_configurations

pytestmark = [pytest.mark.django_db]


def test_user_without_purchases_has_no_configuration(user):
    assert len(get_configurations(recipient=user.email)) == 0


def test_configuration_ordering(factory, configuration, another_configuration, user):
    factory.order(user=user, item=another_configuration.course)
    factory.order(user=user, item=configuration.course)

    assert get_configurations(recipient=user.email)[0] == configuration
    assert get_configurations(recipient=user.email)[1] == another_configuration


def test_another_configuration_ordering(factory, configuration, another_configuration, user):
    factory.order(user=user, item=configuration.course)
    factory.order(user=user, item=another_configuration.course)

    assert get_configurations(recipient=user.email)[0] == another_configuration
    assert get_configurations(recipient=user.email)[1] == configuration
