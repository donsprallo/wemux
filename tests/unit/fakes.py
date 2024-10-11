from wemux import handler
from wemux import message


class FakeCommand(message.Command):
    """A simple mock command."""
    is_handled: bool = False
    data: str | None = None


class FakeCommandHandler(handler.CommandHandler):
    """A simple handler for the mock command. The handler returns the
    command data."""

    def handle(
        self,
        command: FakeCommand
    ) -> str:
        command.is_handled = True
        return command.data


class FakeEvent(message.Event):
    """A simple mock event."""
    is_handled: bool = False


class FakeEventListener(handler.EventListener):
    """A simple event listener for the mock event. The listener set the
    is_called attribute of the event to True."""

    def __init__(self) -> None:
        super().__init__()
        self.is_handled = False

    def handle(
        self,
        event: FakeEvent
    ) -> None:
        self.is_handled = True
        event.is_handled = True
