import pytest

from apps.diplomas.models import Languages

pytestmark = pytest.mark.django_db


@pytest.fixture
def diploma(mixer):
    return mixer.blend("diplomas.Diploma", language=Languages.RU)


@pytest.fixture
def same_en_diploma(diploma, mixer):
    return mixer.blend("diplomas.Diploma", language=Languages.EN, study=diploma.study)


@pytest.mark.parametrize("language", [Languages.EN, Languages.RU])
def test_change_language(as_superuser, diploma, image, language):
    data = {
        "language": language,
    }

    as_superuser.post(f"/admin/diplomas/diploma/{diploma.id}/change/", as_response=True, data=data, format="multipart")

    diploma.refresh_from_db()
    assert diploma.language == data["language"]


def test_err_message_if_diploma_already_exists(as_superuser, diploma, same_en_diploma):
    data = {
        "language": same_en_diploma.language,
    }

    response = as_superuser.post(
        f"/admin/diplomas/diploma/{diploma.id}/change/",
        as_response=True,
        data=data,
        format="multipart",
    )

    assert "Такой диплом уже создан, попробуйте выбрать другой язык." in response.content.decode()
