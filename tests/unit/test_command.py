import pytest

from wemux import dispatcher
from wemux import errors
from wemux import handler
from wemux import message
from wemux import messagebus
from wemux import stream


@pytest.fixture
def mbus():
    """A fixture that returns a message bus."""
    return messagebus.MessageBus(
        dispatcher.InMemoryCommandDispatcher(),
        dispatcher.InMemoryEventDispatcher(),
        stream.InMemoryEventStreamReader()
    )


class TestCommand(message.Command):
    """A simple mock command."""
    is_handled: bool = False
    data: str | None = None


class TestCommandHandler(handler.CommandHandler):
    """A simple handler for the mock command. The handler returns the
    command data."""

    def handle(
        self,
        command: TestCommand
    ) -> str:
        command.is_handled = True
        return command.data


class ExceptionCommandHandler(handler.CommandHandler):
    """A command handler that raises an exception."""

    def handle(
        self,
        command: TestCommand
    ) -> str:
        raise Exception("test")


def test_handle_command_must_call_handler(mbus):
    mbus.add_handler(
        TestCommand,
        TestCommandHandler()
    )
    expected = TestCommand(data="test")
    result: str = mbus.handle(expected)

    assert result == expected.data
    assert expected.is_handled is True


def test_handle_command_must_raise_if_no_handler(mbus):
    cmd = TestCommand(data="not found")
    with pytest.raises(errors.HandlerNotFoundError):
        mbus.handle(cmd)
    assert cmd.is_handled is False


def test_handle_command_must_raise_if_handler_raises(mbus):
    mbus.add_handler(
        TestCommand,
        ExceptionCommandHandler()
    )

    cmd = TestCommand(data="exception")
    with pytest.raises(Exception):
        mbus.handle(cmd)
    assert cmd.is_handled is False


def test_register_handler_must_be_handled(mbus):
    mbus.register_handler(
        TestCommand
    )(TestCommandHandler)

    cmd = TestCommand()
    mbus.handle(cmd)

    assert cmd.is_handled is True
