import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 16:20"),
]


@pytest.fixture(autouse=True)
def material(course, mixer):
    return mixer.blend("notion.Material", course=course, is_home_page=True, page_id="deadbeef")


@pytest.fixture
def another_material(course, mixer, freezer):
    freezer.move_to("2032-12-01 16:40")  # 20 minutes later

    return mixer.blend("notion.Material", course=course, is_home_page=True, page_id="beef")


def test_slug(api):
    got = api.get("/api/v2/studies/purchased/")["results"]

    assert got[0]["home_page_slug"] == "deadbeef"


@pytest.mark.usefixtures("another_material")
def test_latest_material_is_used(api):
    got = api.get("/api/v2/studies/purchased/")["results"]

    assert got[0]["home_page_slug"] == "beef"


def test_material_without_home_page_flag_is_ignored(api, material):
    material.update(is_home_page=False)

    got = api.get("/api/v2/studies/purchased/")["results"]

    assert got[0]["home_page_slug"] is None
