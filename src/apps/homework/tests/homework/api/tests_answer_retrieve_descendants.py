import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase", "_set_current_user"),
]


@pytest.mark.freeze_time("2022-10-09 11:10+12:00")  # +12 hours kamchatka timezone
@pytest.mark.usefixtures("kamchatka_timezone")
def test_descendants(api, answer, mixer, question):
    descendant = mixer.blend("homework.Answer", parent=answer, question=question)

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["has_descendants"] is True
    assert got["descendants"][0]["created"] == "2022-10-09T11:10:00+12:00"
    assert got["descendants"][0]["modified"] == "2022-10-09T11:10:00+12:00"
    assert got["descendants"][0]["slug"] == str(descendant.slug)
    assert got["descendants"][0]["author"]["uuid"] == str(descendant.author.uuid)
    assert got["descendants"][0]["author"]["first_name"] == descendant.author.first_name
    assert got["descendants"][0]["author"]["last_name"] == descendant.author.last_name
    assert got["descendants"][0]["author"]["avatar"] is None
    assert got["descendants"][0]["question"] == str(question.slug)
    assert got["descendants"][0]["has_descendants"] is False
    assert got["descendants"][0]["descendants"] == []
    assert got["descendants"][0]["reactions"] == []


def test_second_level_descendant(api, answer, mixer, question):
    first_level_descendant = mixer.blend("homework.Answer", parent=answer, question=question)
    second_evel_descendant = mixer.blend("homework.Answer", parent=first_level_descendant, question=question)

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["descendants"][0]["slug"] == str(first_level_descendant.slug)
    assert got["descendants"][0]["has_descendants"] is True

    assert got["descendants"][0]["descendants"][0]["slug"] == str(second_evel_descendant.slug)
    assert got["descendants"][0]["descendants"][0]["has_descendants"] is False

