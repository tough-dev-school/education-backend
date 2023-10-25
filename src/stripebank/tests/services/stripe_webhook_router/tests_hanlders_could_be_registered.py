import pytest

from stripebank.services.stripe_webhook_router import stripe_router


@pytest.fixture
def register_handler():
    def define_handler_and_register():
        @stripe_router.register(event_type="test.event")
        def handler_to_register():
            pass

        return handler_to_register

    yield define_handler_and_register
    stripe_router.STRIPE_EVENT_HANDLERS.pop("test.event")


def test_handler_could_be_registered(register_handler):
    registered = register_handler()

    assert "test.event" in stripe_router.STRIPE_EVENT_HANDLERS
    assert stripe_router.STRIPE_EVENT_HANDLERS["test.event"] == registered


def test_handler_could_be_retrieved(register_handler):
    registered = register_handler()

    assert stripe_router.get("test.event") == registered


def test_default_handler_retrieved_if_nothing_matched():
    default_handler = stripe_router.get("test.event")

    assert default_handler == stripe_router.default_handler
