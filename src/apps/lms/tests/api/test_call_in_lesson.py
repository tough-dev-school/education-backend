import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def call(mixer):
    return mixer.blend("lms.Call", name="Обязательный созвон", url="https://skype.icq")


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


def test_both_videos(api, module, call):
    call.update(
        youtube_id="B3EE",
        rutube_id="D4FF",
        rutube_access_key="KFF",
    )

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")["results"][0]["call"]["video"]

    assert got[0]["provider"] == "youtube"
    assert got[1]["provider"] == "rutube"

    assert "B3EE" in got[0]["src"], "youtube src"
    assert "B3EE" in got[0]["embed"], "youtube embed"

    assert "D4FF" in got[1]["src"], "rutube src"
    assert "D4FF" in got[1]["embed"], "rutube embed"

    assert "KFF" in got[1]["src"], "rutube access key"
    assert "KFF" in got[1]["embed"], "rutube access key"


def test_youtube_video(api, module, call):
    call.update(
        youtube_id="B3EE",
    )

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")["results"][0]["call"]["video"]

    assert len(got) == 1
    assert got[0]["provider"] == "youtube"
    assert "B3EE" in got[0]["src"], "youtube src"
    assert "B3EE" in got[0]["embed"], "youtube embed"


def test_rutube_video(api, module, call):
    call.update(
        rutube_id="D4FF",
        rutube_access_key="KFF",
    )

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")["results"][0]["call"]["video"]

    assert len(got) == 1
    assert got[0]["provider"] == "rutube"
    assert "D4FF" in got[0]["src"], "rutube src"
    assert "D4FF" in got[0]["embed"], "rutube embed"
    assert "KFF" in got[0]["src"], "rutube access key"
    assert "KFF" in got[0]["embed"], "rutube access key"
