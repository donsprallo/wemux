import pytest

from wemux import errors
from wemux import messagebus
from .fakes import FakeCommand
from .fakes import FakeCommandHandler
from .fakes import FakeEvent
from .fakes import FakeEventHandler


@pytest.fixture
def mbus():
    """A fixture that returns a message bus."""
    return messagebus.create_in_memory_message_bus()


class TestMessageBusCommandHandler:

    def test_handler_not_found(self, mbus):
        _command = FakeCommand()
        with pytest.raises(errors.HandlerNotFoundError):
            mbus.handle(_command)
        assert _command.is_handled is False

    def test_handle_command_with_error(self, mbus):
        _handler = FakeCommandHandler(err=Exception())
        mbus.subscribe_command(FakeCommand, _handler)

        _expected = FakeCommand()
        with pytest.raises(Exception):
            mbus.handle(_expected)

        assert _expected.is_handled is False
        assert _handler.is_handled is False

    def test_handler_must_be_registered(self, mbus):
        _handler = FakeCommandHandler()
        mbus.subscribe_command(FakeCommand, _handler)

        assert len(mbus._command_handlers) == 1
        assert mbus._command_handlers[FakeCommand] == _handler

    def test_handler_must_be_registered_with_decorator(self, mbus):
        @mbus.subscribe(FakeCommand)
        class TestHandler(FakeCommandHandler):
            pass

        assert len(mbus._command_handlers) == 1
        assert isinstance(mbus._command_handlers[FakeCommand], TestHandler)

    def test_handler_must_be_registered_with_decorator_and_kwargs(self, mbus):
        @mbus.subscribe(FakeCommand, data="test")
        class TestHandler(FakeCommandHandler):
            def __init__(self, stream, data):
                super().__init__(stream)
                self.data = data

        assert len(mbus._command_handlers) == 1
        _handler = mbus._command_handlers[FakeCommand]
        assert isinstance(_handler, TestHandler)
        assert _handler.data == "test"

    def test_handle_command(self, mbus):
        _handler = FakeCommandHandler()
        mbus.subscribe_command(FakeCommand, _handler)

        _expected = FakeCommand()
        mbus.handle(_expected)

        assert _expected.is_handled is True
        assert _handler.is_handled is True

    def test_handle_command_with_data(self, mbus):
        _handler = FakeCommandHandler()
        mbus.subscribe_command(FakeCommand, _handler)

        _expected = FakeCommand(data="test")
        _result = mbus.handle(_expected)

        assert _expected.is_handled is True
        assert _handler.is_handled is True
        assert _result == _expected.data

    def test_handle_events_after_command(self, mbus):
        _event1 = FakeEvent()
        _event2 = FakeEvent()
        _event3 = FakeEvent()
        _handler1 = FakeCommandHandler(
            stream=mbus.events,
            events=[_event1, _event2])
        _handler2 = FakeEventHandler(
            stream=mbus.events,
            events=[_event3])
        mbus.subscribe_command(FakeCommand, _handler1)
        mbus.subscribe_event(FakeEvent, _handler2)

        # The command handler push events to the event stream.
        # The command must return the data of the command.
        _expected = FakeCommand(data="test")
        _result = mbus.handle(_expected)

        assert _expected.is_handled is True
        assert _handler1.is_handled is True
        assert _handler2.is_handled is True
        assert _event1.is_handled is True
        assert _event2.is_handled is True
        assert _event3.is_handled is True
        assert _result == _expected.data


class TestMessageBusEventHandler:

    def test_handler_not_found(self, mbus):
        _event = FakeEvent()
        mbus.emit(_event)
        assert _event.is_handled is False

    def test_must_not_raise_if_handler_raises(self, mbus):
        _handler = FakeEventHandler(err=Exception())
        mbus.subscribe_event(FakeEvent, _handler)

        _event = FakeEvent()
        mbus.emit(_event)

        assert _event.is_handled is False
        assert _handler.is_handled is False

    def test_handler_must_be_registered(self, mbus):
        _handler = FakeEventHandler()
        mbus.subscribe_event(FakeEvent, _handler)

        assert len(mbus._event_handlers[FakeEvent]) == 1
        assert mbus._event_handlers[FakeEvent][0] == _handler

    def test_handler_must_be_registered_with_decorator(self, mbus):
        @mbus.subscribe(FakeEvent)
        class TestHandler(FakeEventHandler):
            pass

        assert len(mbus._event_handlers[FakeEvent]) == 1
        assert isinstance(mbus._event_handlers[FakeEvent][0], TestHandler)

    def test_handler_must_be_registered_with_decorator_and_kwargs(self, mbus):
        @mbus.subscribe(FakeEvent, data="test")
        class TestHandler(FakeEventHandler):
            def __init__(self, stream, data):
                super().__init__(stream)
                self.data = data

        assert len(mbus._event_handlers[FakeEvent]) == 1
        _handler = mbus._event_handlers[FakeEvent][0]
        assert isinstance(_handler, TestHandler)
        assert _handler.data == "test"

    def test_handle_event(self, mbus):
        _handler1 = FakeEventHandler()
        _handler2 = FakeEventHandler()

        mbus.subscribe_event(FakeEvent, _handler1)
        mbus.subscribe_event(FakeEvent, _handler2)

        _expected = FakeEvent()
        mbus.emit(_expected)

        assert _expected.is_handled is True
        assert _handler1.is_handled is True
        assert _handler2.is_handled is True

    def test_handle_events_after_event(self, mbus):
        _event1 = FakeEvent()
        _event2 = FakeEvent()
        _event3 = FakeEvent()
        _handler1 = FakeEventHandler(
            stream=mbus.events,
            events=[_event1, _event2])
        _handler2 = FakeEventHandler(
            stream=mbus.events,
            events=[_event3])
        mbus.subscribe_event(FakeEvent, _handler1)
        mbus.subscribe_event(FakeEvent, _handler2)

        _expected = FakeEvent()
        mbus.emit(_expected)

        assert _expected.is_handled is True
        assert _handler1.is_handled is True
        assert _handler2.is_handled is True
        assert _event1.is_handled is True
        assert _event2.is_handled is True
        assert _event3.is_handled is True
