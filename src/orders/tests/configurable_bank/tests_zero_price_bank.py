import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(course):
    course.setattr_and_save('price', 0)

    return course


def test_zero_price_bank(call_purchase):
    response = call_purchase(desired_bank='zero_price', redirect_url='https://thank.you', as_response=True)

    assert response.status_code == 302
    assert response['Location'] == 'https://thank.you'


def test_fails_with_non_zero_priced_courses(call_purchase, course):
    course.setattr_and_save('price', 100400)

    response = call_purchase(desired_bank='zero_price', redirect_url='https://thank.you', as_response=True)

    assert response.status_code == 400


def test_fails_without_redirect_url(call_purchase):
    response = call_purchase(desired_bank='zero_price', as_response=True)

    assert response.status_code == 400
