import pytest

from homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


def get_answer():
    return Answer.objects.last()


def test_creation(api, question, another_answer):
    api.post(f'/api/v2/homework/questions/{question.slug}/answers/', {
        'text': 'Горите в аду!',
        'parent': another_answer.slug,
    })

    created = get_answer()

    assert created.question == question
    assert created.parent == another_answer
    assert created.author == api.user
    assert created.text == 'Горите в аду!'


def test_without_parent(api, question):
    api.post(f'/api/v2/homework/questions/{question.slug}/answers/', {
        'text': 'Верните деньги!',
    })

    created = get_answer()

    assert created.parent is None


def test_empty_parent(api, question):
    api.post(f'/api/v2/homework/questions/{question.slug}/answers/', {
        'parent': None,
        'text': 'Верните деньги!',
    })

    created = get_answer()

    assert created.parent is None


def test_403_for_not_purchased_users(api, question, purchase):
    purchase.setattr_and_save('paid', None)

    api.post(f'/api/v2/homework/questions/{question.slug}/answers/', {
        'text': 'Верните деньги!',
    }, expected_status_code=403)
