import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase"),
]


@pytest.fixture
def answer_from_another_user(another_user, another_answer, question):
    return another_answer.update(author=another_user, question=question)


@pytest.mark.freeze_time("2022-10-09 10:30:12+12:00")  # +12 hours kamchatka timezone
@pytest.mark.usefixtures("kamchatka_timezone")
def test_ok(api, question, answer):
    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert len(got[0]) == 9
    assert got[0]["created"] == "2022-10-09T10:30:12+12:00"
    assert got[0]["modified"] == "2022-10-09T10:30:12+12:00"
    assert got[0]["slug"] == str(answer.slug)
    assert got[0]["question"] == str(answer.question.slug)
    assert "<em>test</em>" in got[0]["text"]
    assert got[0]["src"] == "*test*"
    assert got[0]["author"]["uuid"] == str(api.user.uuid)
    assert got[0]["author"]["first_name"] == api.user.first_name
    assert got[0]["author"]["last_name"] == api.user.last_name
    assert got[0]["has_descendants"] is False
    assert got[0]["reactions"] == []


def test_has_reaction_fields_if_there_is_reaction(api, question, reaction):
    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    reactions = got[0]["reactions"]
    assert len(reactions[0]) == 4
    assert reactions[0]["emoji"] == reaction.emoji
    assert reactions[0]["slug"] == str(reaction.slug)
    assert reactions[0]["answer"] == str(reaction.answer.slug)
    assert reactions[0]["author"]["uuid"] == str(reaction.author.uuid)
    assert reactions[0]["author"]["first_name"] == reaction.author.first_name
    assert reactions[0]["author"]["last_name"] == reaction.author.last_name


def test_has_descendants_is_true_if_answer_has_children(api, question, answer, another_answer):
    another_answer.update(parent=answer)

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert got[0]["has_descendants"] is True


def test_nplusone(api, question, answer, another_answer, django_assert_num_queries, mixer):
    for _ in range(5):
        mixer.blend("homework.Reaction", author=api.user, answer=answer)
        mixer.blend("homework.Reaction", author=api.user, answer=another_answer)

    with django_assert_num_queries(7):
        api.get(f"/api/v2/homework/answers/?question={question.slug}")


@pytest.mark.usefixtures("answer")
def test_answers_from_other_questions_are_excluded(api, another_question):
    got = api.get(f"/api/v2/homework/answers/?question={another_question.slug}")["results"]

    assert len(got) == 0


def test_non_root_answers_are_excluded(api, question, answer, answer_from_another_user):
    answer.update(parent=answer_from_another_user)

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert len(got) == 1  # only answer_from_another_user
    assert got[0]["slug"] == str(answer_from_another_user.slug)


@pytest.mark.usefixtures("answer", "answer_from_another_user")
def test_answers_from_other_questions_are_excluded_even_if_user_has_the_permission(api, another_question):
    api.user.add_perm("homework.answer.see_all_answers")

    got = api.get(f"/api/v2/homework/answers/?question={another_question.slug}")["results"]

    assert len(got) == 0


@pytest.mark.usefixtures("answer_from_another_user")
def test_answers_from_another_authors_are_excluded(api, question):
    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert len(got) == 0


def test_answers_from_another_authors_are_included_if_already_seen(api, mixer, question, answer_from_another_user):
    mixer.blend("homework.AnswerAccessLogEntry", user=api.user, answer=answer_from_another_user)

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert len(got) == 1


def test_answers_from_another_authors_are_excluded_if_author_is_filtered(api, mixer, question, answer_from_another_user):
    mixer.blend("homework.AnswerAccessLogEntry", user=api.user, answer=answer_from_another_user)

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}&author={api.user.uuid}")["results"]

    assert len(got) == 0


def test_access_log_entries_from_another_users_do_not_break_the_select(api, mixer, question, answer):
    mixer.cycle(5).blend("homework.AnswerAccessLogEntry", question=question, answer=answer)

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert len(got) == 1


@pytest.mark.usefixtures("answer_from_another_user")
def test_users_with_permission_may_see_all_answers(api, question):
    api.user.add_perm("homework.answer.see_all_answers")

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert len(got) == 1


def test_no_anon(anon, question):
    anon.get(f"/api/v2/homework/answers/?question={question.slug}", expected_status_code=401)


@pytest.mark.parametrize(
    "disable_pagination_value",
    [
        "True",
        "true",
        "1",
    ],
)
def test_pagination_could_be_disable_with_query_param(api, question, answer, disable_pagination_value):
    got = api.get(f"/api/v2/homework/answers/?question={question.slug}&disable_pagination={disable_pagination_value}")

    assert len(got) == 1
    assert got[0]["slug"] == str(answer.slug)


@pytest.mark.parametrize(
    "disable_pagination_value",
    [
        "false",
        "False",
        "any-other-value",
    ],
)
@pytest.mark.usefixtures("answer")
def test_paginated_response_with_disable_pagination_false_or_invalid_value(api, question, disable_pagination_value):
    got = api.get(f"/api/v2/homework/answers/?question={question.slug}&disable_pagination={disable_pagination_value}")

    assert "results" in got
    assert "count" in got
    assert len(got["results"]) == 1
