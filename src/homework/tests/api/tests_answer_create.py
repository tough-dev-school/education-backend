import pytest

from homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


@pytest.fixture
def _no_purchase(purchase):
    purchase.setattr_and_save('paid', None)


def get_answer():
    return Answer.objects.last()


def test_creation(api, question, another_answer):
    api.post('/api/v2/homework/answers/', {
        'text': 'Горите в аду!',
        'question': question.slug,
        'parent': another_answer.slug,
    })

    created = get_answer()

    assert created.question == question
    assert created.parent == another_answer
    assert created.author == api.user
    assert created.text == 'Горите в аду!'


def test_without_parent(api, question):
    api.post('/api/v2/homework/answers/', {
        'question': question.slug,
        'text': 'Верните деньги!',
    })

    created = get_answer()

    assert created.parent is None


def test_empty_parent(api, question):
    api.post('/api/v2/homework/answers/', {
        'parent': None,
        'question': question.slug,
        'text': 'Верните деньги!',
    })

    created = get_answer()

    assert created.parent is None


@pytest.mark.xfail(reason='WIP: will per-course permissions later')
@pytest.mark.usefixtures('_no_purchase')
def test_403_for_not_purchased_users(api, question):

    api.post('/api/v2/homework/answers/', {
        'question': question.slug,
        'text': 'Верните деньги!',
    }, expected_status_code=403)


@pytest.mark.usefixtures('_no_purchase')
def test_ok_for_users_with_permission(api, question):
    api.user.add_perm('homework.question.see_all_questions')

    api.post('/api/v2/homework/answers/', {
        'question': question.slug,
        'text': 'Верните деньги!',
    }, expected_status_code=201)


@pytest.mark.usefixtures('_no_purchase')
def test_ok_for_userpusers(api, question):
    api.user.is_superuser = True
    api.user.save()

    api.post('/api/v2/homework/answers/', {
        'question': question.slug,
        'text': 'Верните деньги!',
    }, expected_status_code=201)
