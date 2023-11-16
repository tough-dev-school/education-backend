import pytest
from uuid import uuid4

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def answer_another_user(mixer, question, another_user):
    return mixer.blend("homework.Answer", question=question, author=another_user, text="*test*")


@pytest.fixture
def answer_with_descendants(answer, another_answer, answer_another_user):
    answer_another_user.update(parent=answer)
    another_answer.update(parent=answer_another_user)

    return answer


@pytest.fixture
def get_comments(api):
    return lambda query_params="", *args, **kwargs: api.get(f"/api/v2/homework/comments/{query_params}", *args, **kwargs)


def test_answer_query_param_is_required(get_comments):
    got = get_comments(expected_status_code=400)

    assert "answer" in got


def test_fields(get_comments, answer):
    got = get_comments(f"?answer={answer.slug}")[0]

    assert got["slug"] == str(answer.slug)
    assert got["descendants"] == []  # descendants response tested in tests_comments_list_descendants


def test_return_results_for_several_comma_separated_answers(get_comments, answer, another_answer):
    got = get_comments(f"?answer={answer.slug},{another_answer.slug}")

    assert len(got) == 2


def test_return_comments_for_root_answers_only(get_comments, answer_with_descendants):
    descendent_answer = answer_with_descendants.descendants()[0]

    got = get_comments(f"?answer={descendent_answer.slug}")

    assert len(got) == 0


def test_return_empty_result_for_non_existed_answers(get_comments):
    got = get_comments(f"?answer={uuid4()}")

    assert got == []


def test_exclude_not_allowed_to_access_answers(get_comments, answer_another_user):
    got = get_comments(f"?answer={answer_another_user.slug}")  # answer from another author and not previously accessed

    assert got == []


def test_include_previously_accessed_answers_from_other_authors(api, get_comments, answer_another_user, mixer):
    mixer.blend("homework.AnswerAccessLogEntry", answer=answer_another_user, user=api.user)  # create previous access log

    got = get_comments(f"?answer={answer_another_user.slug}")

    assert len(got) == 1


def test_include_other_authors_user_with_see_all_answers_permissions(get_comments, answer_another_user, api):
    api.user.add_perm("homework.answer.see_all_answers")

    got = get_comments(f"?answer={answer_another_user.slug}")

    assert len(got) == 1


def test_no_anon(anon, answer):
    anon.get(
        f"/api/v2/homework/comments/?answer={answer.slug}/",
        expected_status_code=401,
    )
