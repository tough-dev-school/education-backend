import pytest

pytestmark = [pytest.mark.django_db]


def test_ok(api, module):
    got = api.get(f"/api/v2/lms/modules/{module.pk}/")

    assert got["id"] == module.id
    assert got["name"] == "Первая неделя"
    assert got["description"] == "Самая важная неделя"
    assert got["start_date"] == "2032-12-01T15:30:00+03:00"
    assert got["text"] == "<p>Текст модуля</p>\n"


@pytest.mark.usefixtures("_no_purchase")
def test_404_if_no_purchase(api, module):
    api.get(f"/api/v2/lms/modules/{module.pk}/", expected_status_code=404)


def test_no_anon(anon, module):
    anon.get(f"/api/v2/lms/modules/{module.pk}/", expected_status_code=401)


def test_404_if_hidden_module(api, module):
    module.update(hidden=True)

    api.get(f"/api/v2/lms/modules/{module.pk}/", expected_status_code=404)


@pytest.mark.usefixtures("_no_purchase")
def test_all_visible_for_users_with_permissions(api, module):
    api.user.add_perm("studying.study.purchased_all_courses")
    module.update(hidden=True)

    got = api.get(f"/api/v2/lms/modules/{module.pk}/")

    assert got["id"] == module.id
