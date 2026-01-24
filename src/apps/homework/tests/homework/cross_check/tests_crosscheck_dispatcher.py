import pytest

from apps.homework.models import AnswerCrossCheck

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture()
def admin_user(factory):
    return factory.user()


@pytest.fixture(autouse=True)
def _set_current_user(mocker, admin_user):
    """Dedicated mock to set admin user for later checking authorship"""
    mocker.patch("apps.homework.services.answer_crosscheck_dispatcher.get_current_user", return_value=admin_user)


@pytest.fixture
def dispatcher(answer_dispatcher, answers):
    return answer_dispatcher(answers=answers, answers_per_user=1)


@pytest.mark.repeat(10)
def test_records_are_created(dispatcher, answers, user, another_user):
    dispatcher()

    assert AnswerCrossCheck.objects.filter(answer=answers[0]).exists()
    assert AnswerCrossCheck.objects.filter(answer=answers[1]).exists()

    assert AnswerCrossCheck.objects.filter(checker=user).exists()
    assert AnswerCrossCheck.objects.filter(checker=another_user).exists()


def test_records_are_returned(dispatcher):
    records = dispatcher()

    assert len(records) == 2


def test_authorship(dispatcher, answers, admin_user):
    dispatcher()

    crosscheck = AnswerCrossCheck.objects.get(answer=answers[0])

    assert crosscheck.author == admin_user
