import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('mock_notion_response'),
]


@pytest.mark.parametrize('material_id', ['0e5693d2-173a-4f77-ae81-06813b6e5329', '0e5693d2173a4f77ae8106813b6e5329'])
def test_both_formats_work(api, material_id, mock_notion_response):
    api.get(f'/api/v2/notion/materials/{material_id}/')

    mock_notion_response.assert_called_once_with('0e5693d2173a4f77ae8106813b6e5329')


def test_last_modified_header(api, material):
    got = api.get(f'/api/v2/notion/materials/{material.page_id}/', as_response=True)

    assert got.headers['Last-Modified'] == 'Sun, 16 Jan 2022 21:11:00 UTC'


def test_content_is_passed_from_notion_client(api, material):
    got = api.get(f'/api/v2/notion/materials/{material.page_id}/')

    assert got['block-1']['block-name'] == 'block-1'
    assert got['block-2']['block-name'] == 'block-2'


def test_404_for_non_existant_materials(api, mock_notion_response):
    api.get('/api/v2/notion/materials/nonexistant/', expected_status_code=404)

    mock_notion_response.assert_not_called()


def test_404_for_inactive_materials(api, mock_notion_response, material):
    material.active = False
    material.save()

    api.get('/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/', expected_status_code=404)

    mock_notion_response.assert_not_called()


def test_page_without_last_modified_does_not_break_things(api, material, mocker):
    mocker.patch('notion.block.NotionBlock.last_modified', new_callable=mocker.PropertyMock, return_value=None)

    got = api.get(f'/api/v2/notion/materials/{material.page_id}/', as_response=True)

    assert 'last-modified' not in got.headers
