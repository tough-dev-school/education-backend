import pytest

from apps.mailing.configuration import get_configurations

pytestmark = [pytest.mark.django_db]


def test_user_without_purchases_has_no_configuration(user):
    assert not get_configurations(recipient=user.email).exists()


def test_configuration_ordering(factory, configuration, another_configuration, user):
    factory.order(user=user, item=another_configuration.course)
    factory.order(user=user, item=configuration.course)

    assert get_configurations(recipient=user.email).first() == configuration
    assert get_configurations(recipient=user.email).last() == another_configuration


def test_another_configuration_ordering(factory, configuration, another_configuration, user):
    factory.order(user=user, item=configuration.course)
    factory.order(user=user, item=another_configuration.course)

    assert get_configurations(recipient=user.email).first() == another_configuration
    assert get_configurations(recipient=user.email).last() == configuration
