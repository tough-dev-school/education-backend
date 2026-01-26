import pytest

from apps.notion.models import NotionAsset, Video

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
    pytest.mark.usefixtures(
        "mock_notion_response",
        "_cdn_dev_storage",
    ),
]


@pytest.fixture
def fetched_asset() -> NotionAsset:
    return NotionAsset.objects.create(
        url="secure.notion-static.com/typicalmacuser.jpg",
        file="assets/typicalmacuser-downloaded.jpg",
        size=100,
        md5_sum="D34DBEEF",
    )


@pytest.fixture
def raw_notion_cache_entry(page, material, mixer):
    return mixer.blend(
        "notion.NotionCacheEntry",
        page_id=material.page_id,
        content=page.to_json(),
    )


@pytest.fixture
def get_cached_material(api, raw_notion_cache_entry, mock_notion_response):
    assert raw_notion_cache_entry.content["blocks"][0]["id"] == "block-1"  # make sure cash entry is not ordered

    def _get_cached_material(page_id: str):
        got = api.get(f"/api/v2/materials/{page_id}/")["content"]
        mock_notion_response.assert_not_called()  # make sure we hit the cache

        return got

    return _get_cached_material


@pytest.fixture
def _rutube_video():
    Video.objects.create(
        youtube_id="dVo80vW4ekw",  # check 'page' fixture in notion/conftest
        rutube_id="c30a209fe2e31c0d1513b746e168b1a3",
    )


def test_page_block_goes_first_during_upstream_api_call(api, material):
    """Despite block-3 is the last block, it should be first cuz it the block with type=="page" """
    got = api.get(f"/api/v2/materials/{material.page_id}/")["content"]

    assert list(got.keys())[0] == "block-3"


def test_page_block_goes_first_for_cached_material(get_cached_material, material):
    got = get_cached_material(material.page_id)

    assert list(got.keys())[0] == "block-3"  # page block goes first


def test_extra_tags_are_dropped_during_upstram_api_call(api, material):
    got = api.get(f"/api/v2/materials/{material.page_id}/")["content"]

    assert "_key_to_drop" not in got["block-1"]["value"]


def test_extra_tags_are_dropped_from_cached_material(get_cached_material, material):
    got = get_cached_material(material.page_id)

    assert "_key_to_drop" not in got["block-1"]["value"]


def test_non_fetched_assets_are_rewritten_to_notion_so_urls_during_upstream_api_call(api, material):
    got = api.get(f"/api/v2/materials/{material.page_id}/")["content"]

    assert (
        got["block-3"]["value"]["format"]["page_cover"]
        == "https://notion.so/image/secure.notion-static.com%2Ftypicalmacuser.jpg?table=test-parent-table&id=block-3&cache=v2"
    )


@pytest.mark.usefixtures("fetched_asset")
def test_fetched_assets_paths_are_rewritten_during_upstream_api_call(api, material):
    got = api.get(f"/api/v2/materials/{material.page_id}/")["content"]

    assert got["block-3"]["value"]["format"]["page_cover"] == "https://cdn.tough-dev.school/assets/typicalmacuser-downloaded.jpg"


def test_non_fetched_asset_paths_are_rewritten_to_notion_so_urls_for_cached_material(get_cached_material, material):
    got = get_cached_material(material.page_id)

    assert (
        got["block-3"]["value"]["format"]["page_cover"]
        == "https://notion.so/image/secure.notion-static.com%2Ftypicalmacuser.jpg?table=test-parent-table&id=block-3&cache=v2"
    )


@pytest.mark.usefixtures("fetched_asset")
def test_fetched_asset_paths_are_rewritten_for_cached_material(get_cached_material, material):
    got = get_cached_material(material.page_id)

    assert got["block-3"]["value"]["format"]["page_cover"] == "https://cdn.tough-dev.school/assets/typicalmacuser-downloaded.jpg"


def test_video_is_not_rewrited_by_default(api, material):
    got = api.get(f"/api/v2/materials/{material.page_id}/")["content"]

    assert "youtube" in got["block-video"]["value"]["format"]["display_source"]


@pytest.mark.usefixtures("_rutube_video")
def test_video_is_not_rewritten_for_unknown_country(api, material):
    got = api.get(f"/api/v2/materials/{material.page_id}/")["content"]

    assert "youtube" in got["block-video"]["value"]["format"]["display_source"]


@pytest.mark.usefixtures("_rutube_video")
@pytest.mark.parametrize(
    "ip_addr, should_rewrite",
    [
        ("8.8.8.8", False),
        ("77.88.44.55", True),
        ("212.93.97.105", False),
    ],
)
def test_video_is_not_rewritten_for_russia(api, material, ip_addr, should_rewrite):
    got = api.get(
        f"/api/v2/materials/{material.page_id}/",
        headers={
            "X-Forwarded-For": ip_addr,
        },
    )["content"]

    assert ("rutube" in got["block-video"]["value"]["format"]["display_source"]) is should_rewrite
