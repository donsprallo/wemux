import pytest

from wemux import errors
from wemux import messagebus


class TestCommand(messagebus.Command):
    """A simple mock command."""
    is_handled: bool = False
    data: str | None = None


class TestCommandHandler(messagebus.CommandHandler):
    """A simple handler for the mock command. The handler returns the
    command data."""

    def handle(
            self,
            bus: messagebus.MessageBus,
            command: TestCommand
    ) -> str:
        command.is_handled = True
        return command.data


class ExceptionCommandHandler(messagebus.CommandHandler):
    """A command handler that raises an exception."""

    def handle(
            self,
            bus: messagebus.MessageBus,
            command: TestCommand
    ) -> str:
        raise Exception("test")


def test_handle_command_must_call_handler():
    bus = messagebus.MessageBus()
    bus.add_handler(
        TestCommand,
        TestCommandHandler()
    )

    expected = TestCommand(data="test")
    result: str = bus.handle(expected)

    assert result == expected.data
    assert expected.is_handled is True


def test_handle_command_must_raise_if_no_handler():
    bus = messagebus.MessageBus()

    cmd = TestCommand(data="not found")
    with pytest.raises(errors.CommandHandlerNotFoundError):
        bus.handle(cmd)
    assert cmd.is_handled is False


def test_handle_command_must_raise_if_handler_raises():
    bus = messagebus.MessageBus()
    bus.add_handler(
        TestCommand,
        ExceptionCommandHandler()
    )

    cmd = TestCommand(data="exception")
    with pytest.raises(Exception):
        bus.handle(cmd)
    assert cmd.is_handled is False


def test_register_handler_must_be_handled():
    mbus = messagebus.MessageBus()
    mbus.register_handler(
        TestCommand
    )(TestCommandHandler)

    cmd = TestCommand()
    mbus.handle(cmd)

    assert cmd.is_handled is True
