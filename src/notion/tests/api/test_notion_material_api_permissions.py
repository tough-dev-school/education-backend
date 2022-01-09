import pytest

pytestmark = [pytest.mark.django_db]


def test_no_anon(anon):
    anon.get('/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/', expected_status_code=401)


@pytest.mark.usefixtures('unpaid_order')
def test_404_for_not_purchased_materials(api, fetch_page_recursively):
    api.get('/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/', expected_status_code=404)

    fetch_page_recursively.assert_not_called()


@pytest.mark.usefixtures('unpaid_order')
def test_ok_for_superuser(api):
    api.user.is_superuser = True
    api.user.save()

    api.get('/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/', expected_status_code=200)


@pytest.mark.usefixtures('unpaid_order')
def test_ok_for_user_with_permissions(api):
    api.user.add_perm('notion.material.see_all_materials')

    api.get('/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/', expected_status_code=200)
