import pytest

from homework.models.reaction import Reaction

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def url(answer):
    return f"/api/v2/homework/answers/{answer.slug}/reactions/"


def get_reaction():
    return Reaction.objects.last()


def test_creation(api, url, answer, emoji):
    api.post(url, {"emoji": emoji})

    created = get_reaction()

    assert created.emoji == emoji
    assert created.answer == answer
    assert created.author == api.user


def test_create_reaction_fields(api, url, emoji, answer):
    got = api.post(url, {"emoji": emoji})

    assert len(got) == 4
    assert "-4" in got["slug"]
    assert got["emoji"] == emoji
    assert got["answer"] == str(answer.slug)
    assert got["author"]["uuid"] == str(api.user.uuid)
    assert got["author"]["first_name"] == api.user.first_name
    assert got["author"]["last_name"] == api.user.last_name


@pytest.mark.parametrize("emoji", ["common text", "😄🧑🏿‍🦱", ""])
def test_create_fails_if_not_a_single_emoji(api, url, emoji, answer):
    api.post(url, {"emoji": emoji}, expected_status_code=400)
