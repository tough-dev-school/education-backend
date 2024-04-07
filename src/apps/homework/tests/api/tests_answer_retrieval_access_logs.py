import pytest

from apps.homework.models import AnswerAccessLogEntry

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase"),
]


def get_log_entry():
    return AnswerAccessLogEntry.objects.order_by("-created").first()


@pytest.fixture
def another_author(mixer):
    return mixer.blend("users.User")


@pytest.fixture
def answer(answer, another_author):
    return answer.update(author=another_author)


@pytest.fixture
def api(api):
    """Api as an ordinary student user"""
    api.user.update(is_superuser=False)

    return api


def test_log_entry_is_created(api, answer):
    api.get(f"/api/v2/homework/answers/{answer.slug}/")

    entry = get_log_entry()

    assert entry.user == api.user
    assert entry.answer == answer


def test_terrible_things_does_not_happen_when_there_already_is_a_log_entry_created(api, answer):
    for _ in range(2):
        api.get(f"/api/v2/homework/answers/{answer.slug}/", expected_status_code=200)


def test_log_entry_is_not_created_when_requesting_own_answers(api, answer):
    answer.update(author=api.user)

    api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert get_log_entry() is None


def test_log_entry_is_not_created_for_users_with_permission(api, answer):
    api.user.add_perm("homework.answer.see_all_answers")

    api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert get_log_entry() is None


def test_log_entry_is_not_created_for_superusers(api, answer):
    api.user.update(is_superuser=True)

    api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert get_log_entry() is None
