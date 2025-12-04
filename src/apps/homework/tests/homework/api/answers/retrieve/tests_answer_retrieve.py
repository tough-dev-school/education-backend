from datetime import timedelta

import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase"),
]


@pytest.mark.freeze_time("2022-10-09 11:10+12:00")  # +12 hours kamchatka timezone
@pytest.mark.usefixtures("kamchatka_timezone")
def test_ok(api, answer, question):
    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["created"] == "2022-10-09T11:10:00+12:00"
    assert got["modified"] is None
    assert got["slug"] == str(answer.slug)
    assert got["author"]["uuid"] == str(api.user.uuid)
    assert got["author"]["first_name"] == api.user.first_name
    assert got["author"]["last_name"] == api.user.last_name
    assert got["author"]["avatar"] is None
    assert got["question"] == str(question.slug)
    assert got["has_descendants"] is False
    assert got["descendants"] == []
    assert got["is_editable"] is True
    assert got["reactions"] == []
    assert got["content"]["type"] == "doc"


def test_text_content(api, answer):
    answer.update(content={}, legacy_text="*legacy*")

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["content"] == {}
    assert "legacy" in got["legacy_text"]
    assert "<em>" in got["legacy_text"], "markdown is rendered"


def test_json_content(api, answer):
    answer.update(content={"type": "doc"}, legacy_text="")

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["content"]["type"] == "doc"
    assert got["legacy_text"] == ""


def test_has_descendants_is_true_if_answer_has_children(api, answer, another_answer, another_user):
    another_answer.update(parent=answer, author=another_user)

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["has_descendants"] is True


def test_has_descendants_is_true_if_answer_has_only_children_that_belong_to_its_author(api, answer, another_answer):
    """Раньше это поведение было другим, поэтому я оставляю тест, чтобы задокументировать изменение"""
    another_answer.update(parent=answer, author=answer.author)

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["has_descendants"] is True  # вот тут было False


@pytest.mark.freeze_time("2022-10-09 11:10+12:00")
@pytest.mark.usefixtures("kamchatka_timezone")
@pytest.mark.parametrize(
    ["time", "should_be_editable"],
    [
        ("2022-10-09 11:20+12:00", True),
        ("2032-10-09 11:20+12:00", False),
    ],
)
def test_is_editable_by_time(api, answer, freezer, settings, time, should_be_editable):
    settings.HOMEWORK_ANSWER_EDIT_PERIOD = timedelta(hours=2)
    freezer.move_to(time)

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["is_editable"] is should_be_editable


@pytest.mark.freeze_time("2022-10-09 10:30:12+12:00")  # +12 hours kamchatka timezone
@pytest.mark.usefixtures("kamchatka_timezone")
def test_is_editable_is_only_set_to_author(api, answer, another_user):
    answer.update(author=another_user)

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["is_editable"] is False


def test_reactions_field(api, answer, reaction):
    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert len(got["reactions"]) == 1
    assert got["reactions"][0]["emoji"] == reaction.emoji
    assert got["reactions"][0]["answer"] == str(answer.slug)
    assert got["reactions"][0]["author"]["uuid"] == str(reaction.author.uuid)
    assert got["reactions"][0]["author"]["first_name"] == reaction.author.first_name
    assert got["reactions"][0]["author"]["last_name"] == reaction.author.last_name


def test_query_count_for_answer_without_descendants(api, answer, django_assert_num_queries, mixer):
    for _ in range(25):
        mixer.blend("homework.Reaction", author=api.user, answer=answer)

    with django_assert_num_queries(8):
        api.get(f"/api/v2/homework/answers/{answer.slug}/")


def test_non_root_answers_are_ok(api, answer, another_answer):
    answer.update(parent=another_answer)

    api.get(f"/api/v2/homework/answers/{answer.slug}/", expected_status_code=200)


def test_answers_with_parents_have_parent_field(api, answer, another_answer):
    """Just to document weird behavior of our API: the parent is showed for not root answers only."""
    answer.update(parent=another_answer)

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert "parent" in got


def test_200_for_not_purchased_users(api, answer, purchase, refund):
    refund(purchase)

    api.get(
        f"/api/v2/homework/answers/{answer.slug}/",
        expected_status_code=200,
    )


def test_ok_for_superusers_even_when_they_did_not_purchase_the_course(api, answer, purchase, refund):
    refund(purchase)

    api.user.update(is_superuser=True)

    api.get(
        f"/api/v2/homework/answers/{answer.slug}/",
        expected_status_code=200,
    )


def test_ok_for_users_with_permission_even_when_they_did_not_purchase_the_course(api, answer, purchase, refund):
    refund(purchase)

    api.user.add_perm("homework.question.see_all_questions")

    api.get(
        f"/api/v2/homework/answers/{answer.slug}/",
        expected_status_code=200,
    )


def test_ok_for_answers_of_another_authors(api, answer, mixer):
    answer.update(author=mixer.blend("users.User"))

    api.get(
        f"/api/v2/homework/answers/{answer.slug}/",
        expected_status_code=200,
    )


def test_no_anon(anon, answer):
    anon.get(
        f"/api/v2/homework/answers/{answer.slug}/",
        expected_status_code=401,
    )
