import pytest
from django.db.models import Q
from django.db.utils import IntegrityError

from orders.models.order import Order, only_one_or_zero_is_set

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def record(mixer):
    return mixer.blend('products.Record')


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def bundle(mixer):
    return mixer.blend('products.Bundle')


@pytest.fixture
def student(mixer):
    return mixer.blend('users.User', first_name='Омон', last_name='Кривомазов', gender='male')


def test_only_one_or_zero_is_set():
    cases = [
        Q(
            Q(
                Q(
                    ('bundle__isnull', False),
                    ('course__isnull', True),
                    ('record__isnull', True),
                ),
                Q(
                    ('bundle__isnull', True),
                    ('course__isnull', False),
                    ('record__isnull', True),
                ),
                Q(
                    ('bundle__isnull', True),
                    ('course__isnull', True),
                    ('record__isnull', False),
                ),
                Q(
                    ('bundle__isnull', True),
                    ('course__isnull', True),
                    ('record__isnull', True),
                ),
                _connector='OR',
            ),
        ),
        Q(
            Q(
                Q(
                    ('bundle__isnull', False),
                    ('course__isnull', True),
                ),
                Q(
                    ('bundle__isnull', True),
                    ('course__isnull', False),
                ),
                Q(
                    ('bundle__isnull', True),
                    ('course__isnull', True),
                ),
                _connector='OR',
            ),
        ),
    ]
    expected = [
        only_one_or_zero_is_set('bundle', 'course', 'record'),
        only_one_or_zero_is_set('bundle', 'course'),
    ]

    for i, case in enumerate(cases):
        assert case == expected[i], f'Trouble for the input: {case} != {expected[i]}'


def test_order_constraints_check_product_with_two_items(student, record, course):
    with pytest.raises(IntegrityError):
        Order.objects.create(
            price=100,
            record=record,
            course=course,
            author=student,
            user=student,
        )


def test_order_constraints_check_product_with_three_items(student, course, record, bundle):
    with pytest.raises(IntegrityError):
        Order.objects.create(
            price=100,
            record=record,
            course=course,
            bundle=bundle,
            author=student,
            user=student,
        )
