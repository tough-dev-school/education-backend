import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


def test_patch(api, answer):
    api.patch(f'/api/v2/homework/answers/{answer.slug}/', {'text': 'test'}, expected_status_code=405)


def test_put(api, answer):
    api.put(f'/api/v2/homework/answers/{answer.slug}/', {'text': 'test'}, expected_status_code=405)
