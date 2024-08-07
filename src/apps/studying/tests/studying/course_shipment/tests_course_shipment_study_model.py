import pytest

from apps.studying.models import Study

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def another_order(factory, user, course):
    return factory.order(user=user, item=course)


def test_study_record_is_created(shipment, user, order, course):
    shipment()()

    assert Study.objects.filter(student=user, order=order, course=course).exists()


def test_study_record_is_deleted_when_unshipping(shipment, user, order, course):
    study = Study.objects.create(student=user, order=order, course=course)

    shipment().unship()

    with pytest.raises(Study.DoesNotExist):
        study.refresh_from_db()


def test_study_record_is_ok_even_when_it_already_exists(shipment, user, course, another_order):
    Study.objects.create(student=user, order=another_order, course=course)

    shipment()()
    study_record = Study.objects.get(student=user, course=course)

    assert study_record.order == another_order
