import pytest

from homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


@pytest.fixture
def answer_of_another_author(mixer, question, another_user):
    return mixer.blend('homework.Answer', question=question, author=another_user)


def test_ok(api, answer):
    api.delete(f'/api/v2/homework/answers/{answer.slug}/')

    with pytest.raises(Answer.DoesNotExist):
        answer.refresh_from_db()


def test_can_not_destroy_answer_of_another_author(api, answer_of_another_author):
    api.user.add_perm('homework.answer.see_all_answers')

    api.delete(f'/api/v2/homework/answers/{answer_of_another_author.slug}/', expected_status_code=403)


def test_can_destroy_if_has_permissions(api, answer_of_another_author):
    api.user.add_perm('homework.answer.delete_answer')
    api.user.add_perm('homework.answer.see_all_answers')

    api.delete(f'/api/v2/homework/answers/{answer_of_another_author.slug}/', expected_status_code=204)
