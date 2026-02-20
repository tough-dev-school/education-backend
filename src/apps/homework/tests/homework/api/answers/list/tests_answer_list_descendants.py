import pytest
from django.utils import timezone

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def answer(mixer, api, question):
    return mixer.blend("homework.Answer", author=api.user, question=question, parent=None)


@pytest.mark.usefixtures("comments", "crosschecks")
def test_no_comments_when_crosscheck_is_dispatched_but_user_did_not_perform_it(api, question):
    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert got[0]["has_descendants"] is False


@pytest.mark.usefixtures("comments")
def test_users_without_crosschecks_see_all_descendandts(api, question, crosschecks, another_user):
    crosschecks["to_perform"].update(checker=another_user)

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert got[0]["has_descendants"] is True


@pytest.mark.xfail(strict=True, reason="WIP for @brachkow")
@pytest.mark.usefixtures("comments", "crosschecks")
def test_use_is_able_to_access_his_own_comments_even_when_they_did_not_perform_a_crosscheck(api, mixer, answer):
    mixer.blend("homework.Answer", parent=answer.parent, question=answer.question, author=api.user)

    got = api.get("/api/v2/homework/answers/")

    assert got[0]["has_descendants"] is True


@pytest.mark.usefixtures("comments")
def test_crosscheck_is_performed(api, crosschecks, question):
    crosschecks["to_perform"].update(checked=timezone.now())

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert got[0]["has_descendants"] is True


@pytest.mark.usefixtures("comments", "one_more_crosscheck_that_user_should_perform")
def test_only_one_crosscheck_is_performed(api, question, crosschecks):
    crosschecks["to_perform"].update(checked=timezone.now())  # check only one crosscheck, leaving the second one unchecked

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert got[0]["has_descendants"] is True


@pytest.mark.usefixtures("comments", "one_more_crosscheck_that_user_should_perform")
def test_endpoint_does_not_die_for_users_with_permissions(api, question, crosschecks):
    api.user.add_perm("homework.answer.see_all_answers")
    crosschecks["to_perform"].update(checked=timezone.now())  # check only one crosscheck, leaving the second one unchecked

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert got[0]["has_descendants"] is True


@pytest.mark.usefixtures("comments", "crosschecks")
def test_comments_from_users_with_always_display_comments_are_visible_in_list(api, question, another_user):
    """Users with always_display_comments=True should have their comments visible in list view even when the author hasn't completed crosschecks"""
    another_user.update(always_display_comments=True)

    got = api.get(f"/api/v2/homework/answers/?question={question.slug}")["results"]

    assert got[0]["has_descendants"] is True
