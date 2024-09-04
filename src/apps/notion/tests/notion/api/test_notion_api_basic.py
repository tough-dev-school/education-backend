import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
    pytest.mark.usefixtures(
        "mock_notion_response",
        "_cdn_dev_storage",
    ),
]


@pytest.mark.parametrize("material_id", ["0e5693d2-173a-4f77-ae81-06813b6e5329", "0e5693d2173a4f77ae8106813b6e5329"])
def test_both_formats_work_with_id(api, material_id, mock_notion_response):
    api.get(f"/api/v2/notion/materials/{material_id}/")

    mock_notion_response.assert_called_once_with("0e5693d2173a4f77ae8106813b6e5329")


@pytest.mark.parametrize("material_slug", ["4d5726e8-ee52-4448-b8f9-7be4c7f8e632", "4d5726e8ee524448b8f97be4c7f8e632"])
def test_both_formats_work_with_slug(api, material_slug, mock_notion_response):
    api.get(f"/api/v2/notion/materials/{material_slug}/")

    mock_notion_response.assert_called_once_with("0e5693d2173a4f77ae8106813b6e5329")  # original material id


def test_content_is_passed_from_notion_client(api, material):
    got = api.get(f"/api/v2/notion/materials/{material.page_id}/")

    assert got["block-1"]["value"]["parent_id"] == "100500"
    assert got["block-2"]["value"]["parent_id"] == "100600"


def test_404_for_non_existant_materials(api, mock_notion_response):
    api.get("/api/v2/notion/materials/nonexistant/", expected_status_code=404)

    mock_notion_response.assert_not_called()


def test_404_for_inactive_materials(api, mock_notion_response, material):
    material.update(active=False)

    api.get(f"/api/v2/notion/materials/{material.page_id}/", expected_status_code=404)

    mock_notion_response.assert_not_called()
