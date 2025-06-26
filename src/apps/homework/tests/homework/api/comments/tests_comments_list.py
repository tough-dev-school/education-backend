import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def get_comments(api):
    return lambda query_params="", *args, **kwargs: api.get(f"/api/v2/homework/comments/{query_params}", *args, **kwargs)


def test_500(get_comments):
    get_comments(expected_status_code=500)


def test_no_anon(anon, answer):
    anon.get(
        f"/api/v2/homework/comments/?answer={answer.slug}/",
        expected_status_code=401,
    )
