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
    api.post(url, {"emoji": emoji, "slug": "3fa85f64-5717-4562-b3fc-2c963f66afa6"})

    created = get_reaction()

    assert str(created.slug) == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    assert created.emoji == emoji
    assert created.answer == answer
    assert created.author == api.user


def test_create_reaction_fields(api, url, emoji, answer):
    got = api.post(url, {"emoji": emoji, "slug": "3fa85f64-5717-4562-b3fc-2c963f66afa6"})

    assert len(got) == 4
    assert got["slug"] == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    assert got["emoji"] == emoji
    assert got["answer"] == str(answer.slug)
    assert got["author"]["uuid"] == str(api.user.uuid)
    assert got["author"]["first_name"] == api.user.first_name
    assert got["author"]["last_name"] == api.user.last_name


@pytest.mark.parametrize("emoji", ["common text", "😄🧑🏿‍🦱", ""])
def test_create_fails_if_not_a_single_emoji(api, url, emoji, answer):
    api.post(url, {"emoji": emoji, "slug": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}, expected_status_code=400)


@pytest.mark.parametrize("bad_slug", ["lmao bottom text", "3fa85f64-5717-fake-b3fc-2c963f66afa6", ""])
def test_create_fails_if_not_a_valid_slug(api, url, emoji, answer, bad_slug):
    api.post(url, {"emoji": emoji, "slug": bad_slug}, expected_status_code=400)
