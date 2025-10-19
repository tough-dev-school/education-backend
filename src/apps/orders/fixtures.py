from unittest.mock import patch

import pytest

from apps.orders.models import Order


@pytest.fixture
def refund(user):
    """Sugar to refund an order"""

    def _refund(order: Order, **kwargs):
        with patch("apps.orders.services.order_refunder.get_current_user", return_value=user):
            order.refund(**kwargs)

    return _refund
