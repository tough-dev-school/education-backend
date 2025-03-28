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
