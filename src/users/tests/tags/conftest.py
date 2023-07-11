import pytest


@pytest.fixture
def product_group(factory):
    return factory.group(slug="popug-3")


@pytest.fixture
def course(factory, product_group):
    slug = f"{product_group.slug}-self"
    return factory.course(slug=slug, group=product_group, price=7)


@pytest.fixture
def paid_order(factory, user, course):
    return factory.order(
        is_paid=True,
        user=user,
        item=course,
    )


@pytest.fixture
def non_paid_order(factory, user, course):
    return factory.order(
        is_paid=False,
        user=user,
        item=course,
    )
