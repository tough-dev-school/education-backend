import pytest

pytestmark = [pytest.mark.django_db]


def test_ok(api, module, lesson):
    got = api.get(f"/api/v2/lms/modules/{module.pk}/")

    assert got["id"] == module.id
    assert got["name"] == "Первая неделя"
    assert got["description"] == "Самая важная неделя"
    assert got["start_date"] == "1972-12-01T15:30:00+03:00"
    assert got["has_started"] is True
    assert got["text"] == "<p>Текст модуля</p>\n"
    assert got["lesson_count"] == 1
    assert got["single_lesson_id"] == lesson.pk


@pytest.mark.usefixtures("_no_purchase")
def test_404_if_no_purchase(api, module):
    api.get(f"/api/v2/lms/modules/{module.pk}/", expected_status_code=404)


def test_no_anon(anon, module):
    anon.get(f"/api/v2/lms/modules/{module.pk}/", expected_status_code=401)


def test_404_if_hidden_module(api, module):
    module.update(hidden=True)

    api.get(f"/api/v2/lms/modules/{module.pk}/", expected_status_code=404)


@pytest.mark.usefixtures("_no_purchase")
def test_hidden_modules_are_displayed_for_users_with_permissions(api, module):
    module.update(hidden=True)
    api.user.add_perm("studying.purchased_all_courses")

    got = api.get(f"/api/v2/lms/modules/{module.pk}/")

    assert got["id"] == module.id


@pytest.mark.freeze_time("2032-12-15 12:30:00+03:00")
def test_not_started_modules_are_displayed_for_users_with_permissions(api, module):
    module.update(start_date="2032-12-20 11:11:11+03:00")
    api.user.add_perm("studying.purchased_all_courses")

    got = api.get(f"/api/v2/lms/modules/{module.pk}/")

    assert got["id"] == module.id
    assert got["has_started"] is False


def test_zero_lesson_count(api, module, lesson):
    lesson.delete()
    got = api.get(f"/api/v2/lms/modules/{module.pk}/")

    assert got["lesson_count"] == 0
    assert got["single_lesson_id"] is None


def test_multiple_lesson_count(api, module, lesson, mixer):
    mixer.cycle(3).blend("lms.Lesson", module=lesson.module)

    got = api.get(f"/api/v2/lms/modules/{module.pk}/")

    assert got["lesson_count"] == 4  # existing lesson + 3 generated
    assert got["single_lesson_id"] is None
