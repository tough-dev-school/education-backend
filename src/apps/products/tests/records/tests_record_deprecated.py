import pytest

pytestmark = [pytest.mark.django_db]


def test(mixer):
    with pytest.raises(RuntimeError, match="Deprecated"):
        mixer.blend("products.Record")
