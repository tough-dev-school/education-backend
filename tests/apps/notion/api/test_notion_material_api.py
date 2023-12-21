import pytest
from django.utils import timezone
from datetime import timedelta

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("mock_notion_response"),
]


@pytest.fixture(autouse=True)
def disable_notion_cache(mocker):
    return mocker.patch("apps.notion.cache.should_bypass_cache", return_value=True)


@pytest.fixture
def raw_notion_cache_entry(page, material, mixer):
    return mixer.blend(
        "notion.NotionCacheEntry",
        cache_key=material.page_id,
        content=page.to_json(),
        expires=timezone.now() + timedelta(seconds=10000),
    )


@pytest.fixture
def get_cached_material(api, disable_notion_cache, raw_notion_cache_entry, mock_notion_response):
    disable_notion_cache.return_value = False
    assert raw_notion_cache_entry.content["blocks"][0]["id"] == "block-1"  # make sure cash entry is not ordered

    def _get_cached_material(page_id: str):
        got = api.get(f"/api/v2/notion/materials/{page_id}/")
        mock_notion_response.assert_not_called()  # make sure we hit the cache

        return got

    return _get_cached_material


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


def test_page_block_goes_first_during_upstream_api_call(api, material):
    """Despite block-3 is the last block, it should be first cuz it the block with type=="page" """
    got = api.get(f"/api/v2/notion/materials/{material.page_id}/")

    assert list(got.keys())[0] == "block-3"


def test_page_block_goes_first_for_cached_material(get_cached_material, material):
    got = get_cached_material(material.page_id)

    assert list(got.keys())[0] == "block-3"  # page block goes first


def test_extra_tags_are_dropped_during_upstram_api_call(api, material):
    got = api.get(f"/api/v2/notion/materials/{material.page_id}/")

    assert "_key_to_drop" not in got["block-1"]["value"]


def test_extra_tags_are_dropped_from_cached_material(get_cached_material, material):
    got = get_cached_material(material.page_id)

    assert "_key_to_drop" not in got["block-1"]["value"]


def test_404_for_non_existant_materials(api, mock_notion_response):
    api.get("/api/v2/notion/materials/nonexistant/", expected_status_code=404)

    mock_notion_response.assert_not_called()


def test_404_for_inactive_materials(api, mock_notion_response, material):
    material.update(active=False)

    api.get(f"/api/v2/notion/materials/{material.page_id}/", expected_status_code=404)

    mock_notion_response.assert_not_called()
