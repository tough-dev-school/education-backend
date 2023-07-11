import pytest

from django.utils import timezone


@pytest.fixture
def user(user):
    user.tags = []
    user.save()
    return user


@pytest.fixture
def product_group(factory):
    return factory.group(slug="popug-007")


@pytest.fixture
def course(factory, product_group):
    slug = f"{product_group.slug}-self"
    return factory.course(slug=slug, group=product_group)


@pytest.fixture
def another_course_same_group(factory, product_group):
    return factory.course(group=product_group)


@pytest.fixture
def paid_order(factory, user, course):
    return factory.order(
        user=user,
        paid=timezone.now(),
        unpaid=None,
        shipped=None,
        course=course,
    )


@pytest.fixture
def unpaid_order(factory, user, course):
    return factory.order(
        user=user,
        unpaid=timezone.now(),
        paid=None,
        shipped=None,
        course=course,
    )
