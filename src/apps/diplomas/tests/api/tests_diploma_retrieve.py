import pytest

from apps.diplomas.models import Languages

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def diploma_with_another_lang(mixer, diploma):
    return mixer.blend("diplomas.Diploma", study=diploma.study, language=Languages.RU)


def test(anon, diploma):
    got = anon.get(f"/api/v2/diplomas/{diploma.slug}/")

    assert got["language"] == "EN"
    assert len(got["other_languages"]) == 0
    assert got["slug"] == diploma.slug
    assert got["student"]["uuid"] == str(diploma.study.student.uuid)
    assert got["course"]["name"] == diploma.study.course.name


def test_other_languages(anon, diploma, diploma_with_another_lang):
    got = anon.get(f"/api/v2/diplomas/{diploma.slug}/")

    assert got["other_languages"][0]["slug"] == diploma_with_another_lang.slug
    assert got["other_languages"][0]["language"] == "RU"
    assert got["other_languages"][0]["student"]["uuid"] == str(diploma_with_another_lang.study.student.uuid)
    assert got["other_languages"][0]["course"]["name"] == diploma_with_another_lang.study.course.name


def test_no_diplomas_from_another_students(anon, diploma, diploma_with_another_lang, mixer):
    diploma_with_another_lang.update(study=mixer.blend("studying.Study"))

    got = anon.get(f"/api/v2/diplomas/{diploma.slug}/")

    assert len(got["other_languages"]) == 0
