import pytest


@pytest.fixture
def mock_item_unshipping(mocker):
    return mocker.patch("studying.shipment_factory.unship")
