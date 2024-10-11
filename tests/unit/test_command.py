import pytest

from tests.unit.fakes import FakeCommand
from tests.unit.fakes import FakeCommandHandler
from wemux import errors
from wemux import handler
from wemux import messagebus


@pytest.fixture
def mbus():
    """A fixture that returns a message bus."""
    return messagebus.create_in_memory_message_bus()


class ExceptionCommandHandler(handler.CommandHandler):
    """A command handler that raises an exception."""

    def handle(
        self,
        command: FakeCommand
    ) -> str:
        raise Exception("test")


def test_handle_command_must_call_handler(mbus):
    mbus.add_handler(
        FakeCommand,
        FakeCommandHandler()
    )
    expected = FakeCommand(data="test")
    result: str = mbus.handle(expected)

    assert result == expected.data
    assert expected.is_handled is True


def test_handle_command_must_raise_if_no_handler(mbus):
    cmd = FakeCommand(data="not found")
    with pytest.raises(errors.HandlerNotFoundError):
        mbus.handle(cmd)
    assert cmd.is_handled is False


def test_handle_command_must_raise_if_handler_raises(mbus):
    mbus.add_handler(
        FakeCommand,
        ExceptionCommandHandler()
    )

    cmd = FakeCommand(data="exception")
    with pytest.raises(Exception):
        mbus.handle(cmd)
    assert cmd.is_handled is False


def test_register_handler_must_be_handled(mbus):
    mbus.register_handler(
        FakeCommand
    )(FakeCommandHandler)

    cmd = FakeCommand()
    mbus.handle(cmd)

    assert cmd.is_handled is True
