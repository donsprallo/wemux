import pytest

from wemux import dispatcher
from wemux import handler
from wemux import message
from wemux import messagebus


@pytest.fixture
def mbus():
    """A fixture that returns a message bus."""
    return messagebus.MessageBus(
        dispatcher.LocalCommandDispatcher(),
        dispatcher.LocalEventDispatcher()
    )


class TestEvent(message.Event):
    """A simple mock event."""
    is_handled: bool = False


class TestEventListener(handler.EventListener):
    """A simple event listener for the mock event. The listener set the
    is_called attribute of the event to True."""

    def __init__(self) -> None:
        super().__init__()
        self.is_handled = False

    def handle(
        self,
        event: TestEvent
    ) -> None:
        self.is_handled = True
        event.is_handled = True


def test_handle_event_must_call_listener(mbus):
    listener1 = TestEventListener()
    listener2 = TestEventListener()

    mbus.add_listener(
        TestEvent,
        listener1
    )

    mbus.add_listener(
        TestEvent,
        listener2
    )

    expected = TestEvent()
    mbus.emit(expected)

    assert expected.is_handled is True
    assert listener1.is_handled is True
    assert listener2.is_handled is True
