import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def call(mixer):
    return mixer.blend(
        "lms.Call",
        name="Обязательный созвон",
        description="Не пропустите",
        url="https://skype.icq",
        datetime="2032-12-01 15:30:44 +03:00",
    )


@pytest.fixture
def material(mixer):
    return mixer.blend("notion.Material", title="Урок 3")


@pytest.fixture
def question(mixer):
    return mixer.blend(
        "homework.Question",
        text="Составьте *математическую модель* каждого атома в атмосфере Земли на год вперед, учитывая все возможные взаимодействия и условия.",
    )


def test_ok(api, lesson):
    got = api.get(f"/api/v2/lms/lessons/{lesson.pk}/")

    assert got["id"] == lesson.id
    assert got["material"] is None
    assert got["call"] is None


@pytest.mark.usefixtures("_no_purchase")
def test_404_if_no_purchase(api, lesson):
    api.get(f"/api/v2/lms/lessons/{lesson.pk}/", expected_status_code=404)


def test_no_anon(anon, lesson):
    anon.get(f"/api/v2/lms/lessons/{lesson.pk}/", expected_status_code=401)


def test_call(api, lesson, call):
    lesson.update(call=call)

    got = api.get(f"/api/v2/lms/lessons/{lesson.pk}/")

    assert got["id"] == lesson.id
    assert got["call"]["name"] == "Обязательный созвон"
    assert got["call"]["description"] == "Не пропустите"
    assert got["call"]["url"] == "https://skype.icq"
    assert got["call"]["datetime"] == "2032-12-01T15:30:44+03:00"


def test_material(api, lesson, material):
    lesson.update(material=material)

    got = api.get(f"/api/v2/lms/lessons/{lesson.pk}/")

    assert got["id"] == lesson.id
    assert got["material"]["id"] == str(material.slug).replace("-", "")
    assert got["material"]["title"] == "Урок 3"


def test_question(api, lesson, question):
    lesson.update(question=question)

    got = api.get(f"/api/v2/lms/lessons/{lesson.pk}/")

    assert got["homework"]["question"]["name"] == question.name
