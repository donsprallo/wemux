from wemux import messagebus


class TestEvent(messagebus.Event):
    """A simple mock event."""
    is_handled: bool = False


class TestEventListener(messagebus.EventListener):
    """A simple event listener for the mock event. The listener set the
    is_called attribute of the event to True."""

    def __init__(self) -> None:
        super().__init__()
        self.is_handled = False

    def handle(
            self,
            bus: messagebus.MessageBus,
            event: TestEvent
    ) -> None:
        self.is_handled = True
        event.is_handled = True


def test_handle_event_must_call_listener():
    bus = messagebus.MessageBus()

    listener1 = TestEventListener()
    listener2 = TestEventListener()

    bus.add_listener(
        TestEvent,
        listener1
    )

    bus.add_listener(
        TestEvent,
        listener2
    )

    expected = TestEvent()
    bus.emit(expected)

    assert expected.is_handled is True
    assert listener1.is_handled is True
    assert listener2.is_handled is True
