import pytest

from apps.notion.models import Video
from apps.notion.rewrite import rewrite_video
from apps.notion.types import BlockValue

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


def rewrite(block) -> BlockValue:
    return rewrite_video(block)["value"]


@pytest.fixture(autouse=True)
def _video_mapping():
    Video.objects.create(
        youtube_id="dVo80vW4ekw",
        rutube_id="c30a209fe2e31c0d1513b746e168b1a3",
    )


def test_non_youtube_video(non_youtube_video):
    assert rewrite(non_youtube_video) == non_youtube_video["value"]  # should be unchanged


def test_rewritten(youtube_video):
    result = rewrite(youtube_video)

    assert result["properties"]["source"] == [["https://rutube.ru/video/c30a209fe2e31c0d1513b746e168b1a3/"]]  # Video source
    assert result["format"]["display_source"] == "https://rutube.ru/play/embed/c30a209fe2e31c0d1513b746e168b1a3/"  # embed
    assert result["format"]["link_provider"] == "RuTube"


def test_not_rewritten(youtube_video):
    Video.objects.all().delete()

    result = rewrite(youtube_video)

    assert result["properties"]["source"] == [["https://youtu.be/dVo80vW4ekw"]]
    assert result["format"]["display_source"] == "https://www.youtube.com/embed/dVo80vW4ekw?rel=0"
    assert result["format"]["link_provider"] == "YouTube"


def test_private_video(youtube_video):
    Video.objects.all().update(rutube_access_key="10K7TJntZwspv8QViYHMwg")

    result = rewrite(youtube_video)

    assert result["properties"]["source"] == [["https://rutube.ru/video/c30a209fe2e31c0d1513b746e168b1a3/?p=10K7TJntZwspv8QViYHMwg"]]
    assert result["format"]["display_source"] == "https://rutube.ru/play/embed/c30a209fe2e31c0d1513b746e168b1a3/?p=10K7TJntZwspv8QViYHMwg"
    assert result["format"]["link_provider"] == "RuTube"
