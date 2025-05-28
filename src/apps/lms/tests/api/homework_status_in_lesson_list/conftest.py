import pytest


@pytest.fixture(autouse=True)
def question(mixer, lesson):
    question = mixer.blend(
        "homework.Question",
        text="Составьте *математическую модель* каждого атома в атмосфере Земли на год вперед, учитывая все возможные взаимодействия и условия.",
    )
    lesson.update(question=question)

    return question


@pytest.fixture
def another_question(mixer):
    question = mixer.blend(
        "homework.Question",
    )

    return question


@pytest.fixture
def answer(mixer, api, question):
    return mixer.blend(
        "homework.Answer",
        author=api.user,
        question=question,
        parent_id=None,
    )


@pytest.fixture
def another_answer(mixer, question, another_user):
    return mixer.blend(
        "homework.Answer",
        question=question,
        parent_id=None,
        author=another_user,
    )
