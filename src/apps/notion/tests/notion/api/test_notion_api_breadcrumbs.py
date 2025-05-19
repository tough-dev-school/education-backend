import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
    pytest.mark.usefixtures(
        "mock_notion_response",
        "_cdn_dev_storage",
    ),
]


@pytest.fixture
def module(factory, course):
    return factory.module(course=course)


@pytest.fixture
def lesson(factory, module, material):
    return factory.lesson(module=module, material=material)


@pytest.fixture
def another_course(factory):
    return factory.course()


def test_empty_breadcrumbs(api, material):
    """Despite block-3 is the last block, it should be first cuz it the block with type=="page" """
    got = api.get(f"/api/v2/materials/{material.page_id}/")

    assert got["breadcrumbs"] == {}


def test_bredcrumbs(api, material, lesson, course):
    got = api.get(f"/api/v2/materials/{material.page_id}/")

    assert got["breadcrumbs"]["course"]["slug"] == course.slug
    assert got["breadcrumbs"]["module"]["id"] == lesson.module.id
    assert got["breadcrumbs"]["lesson"]["id"] == lesson.id


def test_course_mismatch_for_lesson_and_material(api, material, another_course, lesson):
    lesson.module.update(course=another_course)

    got = api.get(f"/api/v2/materials/{material.page_id}/")

    assert got["breadcrumbs"] == {}
