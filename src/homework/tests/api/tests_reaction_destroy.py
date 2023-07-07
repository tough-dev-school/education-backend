import pytest

from homework.models.reaction import Reaction

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def reaction_of_another_author(mixer, answer, another_user):
    return mixer.blend("homework.Reaction", answer=answer, author=another_user)


@pytest.fixture
def url(answer):
    return f"/api/v2/homework/answers/{answer.slug}/reactions/"


def test_ok(api, url, reaction):
    api.delete(f"{url}{reaction.slug}/")

    with pytest.raises(Reaction.DoesNotExist):
        reaction.refresh_from_db()


def test_can_not_destroy_answer_of_another_author(api, url, reaction_of_another_author):
    api.delete(f"{url}{reaction_of_another_author.slug}/", expected_status_code=403)
