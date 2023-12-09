import pytest

@pytest.fixture
def course(factory):
    return factory.course(
        slug="aa-5-full",
        name="Как стать таким же умным как Антон Давыдов",
    )
