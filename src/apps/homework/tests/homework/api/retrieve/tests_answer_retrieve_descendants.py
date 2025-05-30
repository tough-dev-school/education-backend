import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase", "_set_current_user"),
]


@pytest.fixture
def comments(answer, mixer, another_user):
    return mixer.cycle(2).blend("homework.Answer", parent=answer, question=answer.question, author=another_user)


@pytest.fixture
def crosscheck_that_user_should_perform(mixer, answer):
    return mixer.blend(
        "homework.AnswerCrossCheck",
        checker=answer.author,
        answer=mixer.blend("homework.Answer", question=answer.question),
        checked=None,
    )


@pytest.fixture
def one_more_crosscheck_that_user_should_perform(mixer, answer):
    return mixer.blend(
        "homework.AnswerCrossCheck",
        checker=answer.author,
        answer=mixer.blend("homework.Answer", question=answer.question),
        checked=None,
    )


@pytest.fixture
def crosscheck_that_user_should_recieve(mixer, answer, another_user):
    return mixer.blend(
        "homework.AnswerCrossCheck",
        checker=another_user,
        answer=answer,
        checked=None,
    )


@pytest.fixture
def crosschecks(crosscheck_that_user_should_recieve, crosscheck_that_user_should_perform):
    return {
        "recieved": crosscheck_that_user_should_recieve,
        "to_perform": crosscheck_that_user_should_perform,
    }


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
