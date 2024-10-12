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

    def test_handler_must_raise_if_handler_raises(self, mbus):
        _handler = FakeCommandHandler(Exception())
        _command = FakeCommand(data="exception")

        mbus.register_command_handler(
            FakeCommand, _handler)

        with pytest.raises(Exception):
            mbus.handle(_command)
        assert _command.is_handled is False

    def test_handler_must_be_registered(self, mbus):
        handler = FakeCommandHandler()
        mbus.register_command_handler(FakeCommand, handler)

        assert len(mbus._command_handlers) == 1
        assert mbus._command_handlers[FakeCommand] == handler

    def test_handler_must_be_registered_with_decorator(self, mbus):
        @mbus.register_handler(FakeCommand)
        class Handler(FakeCommandHandler):
            pass

        assert len(mbus._command_handlers) == 1
        assert isinstance(mbus._command_handlers[FakeCommand], Handler)

    def test_handler_must_be_registered_with_decorator_and_kwargs(self, mbus):
        @mbus.register_handler(FakeCommand, data="test")
        class Handler(FakeCommandHandler):
            def __init__(self, data):
                super().__init__()
                self.data = data

        assert len(mbus._command_handlers) == 1
        _handler = mbus._command_handlers[FakeCommand]
        assert isinstance(_handler, Handler)
        assert _handler.data == "test"

    def test_handle_command(self, mbus):
        handler = FakeCommandHandler()
        mbus.register_command_handler(FakeCommand, handler)

        expected = FakeCommand()
        mbus.handle(expected)

        assert expected.is_handled is True
        assert handler.is_handled is True


class TestMessageBusEventHandler:

    def test_handler_not_found(self, mbus):
        event = FakeEvent()
        mbus.emit(event)
        assert event.is_handled is False

    def test_handler_must_be_registered(self, mbus):
        handler = FakeEventHandler()
        mbus.register_event_handler(FakeEvent, handler)

        assert len(mbus._event_handlers[FakeEvent]) == 1
        assert mbus._event_handlers[FakeEvent][0] == handler

    def test_handler_must_be_registered_with_decorator(self, mbus):
        @mbus.register_handler(FakeEvent)
        class Handler(FakeEventHandler):
            pass

        assert len(mbus._event_handlers[FakeEvent]) == 1
        assert isinstance(mbus._event_handlers[FakeEvent][0], Handler)

    def test_handler_must_be_registered_with_decorator_and_kwargs(self, mbus):
        @mbus.register_handler(FakeEvent, data="test")
        class Handler(FakeEventHandler):
            def __init__(self, data):
                super().__init__()
                self.data = data

        assert len(mbus._event_handlers[FakeEvent]) == 1
        _handler = mbus._event_handlers[FakeEvent][0]
        assert isinstance(_handler, Handler)
        assert _handler.data == "test"

    def test_handle_event(self, mbus):
        handler1 = FakeEventHandler()
        handler2 = FakeEventHandler()

        mbus.register_event_handler(FakeEvent, handler1)
        mbus.register_event_handler(FakeEvent, handler2)

        expected = FakeEvent()
        mbus.emit(expected)

        assert expected.is_handled is True
        assert handler1.is_handled is True
        assert handler2.is_handled is True
