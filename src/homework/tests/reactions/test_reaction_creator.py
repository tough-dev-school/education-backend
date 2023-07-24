import pytest

from emoji import EMOJI_DATA

from homework.models.reaction import Reaction
from homework.services import ReactionCreator
from homework.services.reaction_creator import ReactionCreatorException

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def create():
    return lambda *args, **kwargs: ReactionCreator(*args, **kwargs)()


@pytest.fixture
def emoji_list():
    return list(EMOJI_DATA.keys())


@pytest.fixture
def emoji(emoji_list):
    return emoji_list[-1]


@pytest.mark.parametrize("emoji", ["👌", "🐍", "🧑🏿‍🦱", "👨‍👨‍👧‍👧"])
def test_success_creation(create, user, answer, emoji):
    reaction = create(emoji=emoji, author=user, answer=answer)

    assert reaction.emoji == emoji
    assert reaction.author == user
    assert reaction.answer == answer


def test_creation_with_custom_slug(create, user, answer):
    reaction = create(emoji="👌", slug="3fa85f64-5717-4562-b3fc-2c963f66afa6", author=user, answer=answer)

    assert str(reaction.slug) == "3fa85f64-5717-4562-b3fc-2c963f66afa6"


@pytest.mark.parametrize("emoji", ["👌🐍", "snake🐍", "🏝️rest", "🙃🙂", "✄"])
def test_fail_if_not_a_single_emoji(create, user, answer, emoji):
    with pytest.raises(ReactionCreatorException, match="Invalid emoji symbol"):
        create(emoji=emoji, author=user, answer=answer)


def test_fail_if_user_rich_limit(create, user, answer, emoji_list):
    limit = Reaction.MAX_REACTIONS_FROM_ONE_AUTHOR
    for i in range(limit):
        create(emoji=emoji_list[i], author=user, answer=answer)

    with pytest.raises(ReactionCreatorException, match=f"Only {limit} reactions per answer are allowed from one author."):
        create(emoji=emoji_list[limit], author=user, answer=answer)


def test_fail_if_user_made_same_reaction(create, user, answer, emoji):
    create(emoji=emoji, author=user, answer=answer)

    with pytest.raises(ReactionCreatorException, match="Unique emoji per author"):
        create(emoji=emoji, author=user, answer=answer)
