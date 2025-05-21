import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def call(mixer):
    return mixer.blend("lms.Call", name="Обязательный созвон", url="https://skype.icq")


@pytest.fixture
def _youtube_video(call):
    call.update(
        youtube_id="B3EE",
    )


@pytest.fixture
def _rutube_video(call):
    call.update(
        rutube_id="D4FF",
        rutube_access_key="KFF",
    )


@pytest.fixture(autouse=True)
def lesson(lesson, call):
    lesson.update(call=call)

    return lesson


def test_no_call(api, module, lesson):
    lesson.update(call=None)
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["call"] is None


def test_call(api, module, lesson):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["call"]["name"] == "Обязательный созвон"
    assert got["results"][0]["call"]["url"] == "https://skype.icq"


def test_empty_video(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["call"]["video"] == []


@pytest.mark.usefixtures("_youtube_video", "_rutube_video")
def test_both_videos(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")["results"][0]["call"]["video"]

    assert got[0]["provider"] == "youtube"
    assert got[1]["provider"] == "rutube"

    assert "B3EE" in got[0]["src"], "youtube src"
    assert "B3EE" in got[0]["embed"], "youtube embed"

    assert "D4FF" in got[1]["src"], "rutube src"
    assert "D4FF" in got[1]["embed"], "rutube embed"

    assert "KFF" in got[1]["src"], "rutube access key"
    assert "KFF" in got[1]["embed"], "rutube access key"


@pytest.mark.usefixtures("_youtube_video")
def test_youtube_video(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")["results"][0]["call"]["video"]

    assert len(got) == 1
    assert got[0]["provider"] == "youtube"
    assert "B3EE" in got[0]["src"], "youtube src"
    assert "B3EE" in got[0]["embed"], "youtube embed"


@pytest.mark.usefixtures("_rutube_video")
def test_rutube_video(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")["results"][0]["call"]["video"]

    assert len(got) == 1
    assert got[0]["provider"] == "rutube"
    assert "D4FF" in got[0]["src"], "rutube src"
    assert "D4FF" in got[0]["embed"], "rutube embed"
    assert "KFF" in got[0]["src"], "rutube access key"
    assert "KFF" in got[0]["embed"], "rutube access key"


@pytest.mark.usefixtures("_youtube_video", "_rutube_video")
def test_recommended_video_provider_by_default(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")["results"][0]["call"]

    assert got["recommended_video_provider"] == "youtube"


@pytest.mark.usefixtures("_rutube_video")
def test_rutube_only(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")["results"][0]["call"]

    assert got["recommended_video_provider"] == "rutube"


@pytest.mark.parametrize(
    ("country", "expected_provider"),
    [
        ("RU", "rutube"),
        ("PL", "youtube"),
    ],
)
@pytest.mark.usefixtures("_youtube_video", "_rutube_video")
def test_country_based_rewriting(api, module, country, expected_provider):
    got = api.get(
        f"/api/v2/lms/lessons/?module={module.pk}",
        headers={
            "cf-ipcountry": country,
        },
    )["results"][0]["call"]

    assert got["recommended_video_provider"] == expected_provider


@pytest.mark.usefixtures("_youtube_video")
def test_youtube_only(api, module):
    got = api.get(
        f"/api/v2/lms/lessons/?module={module.pk}",
        headers={
            "cf-ipcountry": "RU",
        },
    )["results"][0]["call"]

    assert got["recommended_video_provider"] == "youtube"
