import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def material(mixer):
    return mixer.blend("notion.Material", title="Урок 3")


def test_no_material(api, module, lesson):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["material"] is None


def test_attachmed_material(api, module, lesson, material):
    lesson.update(material=material)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["material"]["id"] == str(material.slug).replace("-", "")
    assert got["results"][0]["material"]["title"] == "Урок 3"
