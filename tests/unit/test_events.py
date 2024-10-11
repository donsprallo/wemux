import pytest

from tests.unit.fakes import FakeEvent
from tests.unit.fakes import FakeEventListener
from wemux import messagebus


@pytest.fixture
def mbus():
    """A fixture that returns a message bus."""
    return messagebus.create_in_memory_message_bus()


def test_handle_event_must_call_listener(mbus):
    listener1 = FakeEventListener()
    listener2 = FakeEventListener()

    mbus.add_listener(
        FakeEvent,
        listener1
    )

    mbus.add_listener(
        FakeEvent,
        listener2
    )

    expected = FakeEvent()
    mbus.emit(expected)

    assert expected.is_handled is True
    assert listener1.is_handled is True
    assert listener2.is_handled is True
