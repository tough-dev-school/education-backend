import pytest

from onetime.models import Token

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.fixture
def token(mixer):
    return lambda **kwargs: mixer.blend('onetime.Token', **kwargs)


@pytest.mark.parametrize('expires, is_active', [
    [None, True],
    ['2032-12-05', True],
    ['2032-11-05', False],
])
def test(token, expires, is_active):
    token = token(expires=expires)

    assert (token in Token.objects.active()) is is_active
