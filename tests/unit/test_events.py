import pytest

from wemux import messagebus
from .fakes import FakeEvent
from .fakes import FakeEventHandler


@pytest.fixture
def mbus():
    """A fixture that returns a message bus."""
    return messagebus.create_in_memory_message_bus()


def test_handle_event_must_call_listener(mbus):
    handler1 = FakeEventHandler()
    handler2 = FakeEventHandler()

    mbus.add_listener(
        FakeEvent,
        handler1
    )

    mbus.add_listener(
        FakeEvent,
        handler2
    )

    expected = FakeEvent()
    mbus.emit(expected)

    assert expected.is_handled is True
    assert handler1.is_handled is True
    assert handler2.is_handled is True
