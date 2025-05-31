import pytest
from django.utils import timezone

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase", "_set_current_user"),
]


@pytest.mark.freeze_time("2022-10-09 11:10+12:00")  # +12 hours kamchatka timezone
@pytest.mark.usefixtures("kamchatka_timezone")
def test_descendants(api, answer, question, comments):
    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["has_descendants"] is True
    assert got["descendants"][0]["created"] == "2022-10-09T11:10:00+12:00"
    assert got["descendants"][0]["modified"] == "2022-10-09T11:10:00+12:00"
    assert got["descendants"][0]["slug"] == str(comments[0].slug)
    assert got["descendants"][0]["author"]["uuid"] == str(comments[0].author.uuid)
    assert got["descendants"][0]["author"]["first_name"] == comments[0].author.first_name
    assert got["descendants"][0]["author"]["last_name"] == comments[0].author.last_name
    assert got["descendants"][0]["author"]["avatar"] is None
    assert got["descendants"][0]["question"] == str(question.slug)
    assert got["descendants"][0]["has_descendants"] is False
    assert got["descendants"][0]["descendants"] == []
    assert got["descendants"][0]["reactions"] == []


def test_second_level_descendant(api, answer, mixer, question, comments):
    first_level_descendant = comments[0]
    second_evel_descendant = mixer.blend("homework.Answer", parent=first_level_descendant, question=question)

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["descendants"][0]["slug"] == str(first_level_descendant.slug)
    assert got["descendants"][0]["has_descendants"] is True

    assert got["descendants"][0]["descendants"][0]["slug"] == str(second_evel_descendant.slug)
    assert got["descendants"][0]["descendants"][0]["has_descendants"] is False


@pytest.mark.usefixtures("comments", "crosschecks")
def test_no_comments_when_crosscheck_is_dispatched_but_user_did_not_perform_it(api, answer):
    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["has_descendants"] is False
    assert got["descendants"] == []


@pytest.mark.usefixtures("comments")
def test_user_has_performed_a_crosscheck_and_now_may_access_all_answers(api, answer, crosschecks, another_user):
    crosschecks["to_perform"].update(checker=another_user)
    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["has_descendants"] is True
    assert len(got["descendants"]) == 2


@pytest.mark.xfail(strict=True, reason="WIP for @brachkow")
@pytest.mark.usefixtures("comments", "crosschecks")
def test_use_is_able_to_access_his_own_comments_even_when_they_did_not_perform_a_crosscheck(api, answer, mixer):
    mixer.blend("homework.Answer", parent=answer.parent, question=answer.question, author=api.user)

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["has_descendants"] is True
    assert len(got["descendants"]) == 1


def test_crosscheck_is_performed(api, answer, crosschecks, comments):
    crosschecks["to_perform"].update(checked=timezone.now())

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert len(got["descendants"]) == 2
    assert got["descendants"][0]["slug"] == str(comments[0].slug)
    assert got["descendants"][1]["slug"] == str(comments[1].slug)


@pytest.mark.usefixtures("comments", "one_more_crosscheck_that_user_should_perform")
def test_only_one_crosscheck_is_performed(api, answer, crosschecks):
    crosschecks["to_perform"].update(checked=timezone.now())  # check only one crosscheck, leaving the second one unchecked

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert len(got["descendants"]) == 1


@pytest.mark.usefixtures("comments", "one_more_crosscheck_that_user_should_perform")
def test_user_with_permissions_may_access_all_comments_event_when_they_did_not_perform_a_crosscheck(api, answer, crosschecks):
    api.user.add_perm("homework.answer.see_all_answers")
    crosschecks["to_perform"].update(checked=timezone.now())  # check only one crosscheck, leaving the second one unchecked

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert len(got["descendants"]) == 2
