import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def call(mixer):
    return mixer.blend("lms.Call", name="Обязательный созвон", url="https://skype.icq")


def test_no_call(api, module, lesson):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["call"] is None


def test_call(api, module, lesson, call):
    lesson.update(call=call)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["call"]["name"] == "Обязательный созвон"
    assert got["results"][0]["call"]["url"] == "https://skype.icq"
