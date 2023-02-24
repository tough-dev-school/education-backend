import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('mock_notion_response'),
]


@pytest.mark.parametrize('material_id', ['0e5693d2-173a-4f77-ae81-06813b6e5329', '0e5693d2173a4f77ae8106813b6e5329'])
def test_both_formats_work(api, material_id, mock_notion_response):
    api.get(f'/api/v2/notion/materials/{material_id}/')

    mock_notion_response.assert_called_once_with('0e5693d2173a4f77ae8106813b6e5329')


def test_content_is_passed_from_notion_client(api, material):
    got = api.get(f'/api/v2/notion/materials/{material.page_id}/')

    assert got['block-1']['role'] == 'reader-1'
    assert got['block-2']['role'] == 'reader-2'


def test_404_for_non_existant_materials(api, mock_notion_response):
    api.get('/api/v2/notion/materials/nonexistant/', expected_status_code=404)

    mock_notion_response.assert_not_called()


def test_404_for_inactive_materials(api, mock_notion_response, material):
    material.active = False
    material.save()

    api.get('/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/', expected_status_code=404)

    mock_notion_response.assert_not_called()
