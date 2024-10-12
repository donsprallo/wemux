from wemux import handler
from wemux import message


class FakeCommand(message.Command):
    """A simple mock command."""
    is_handled: bool = False
    data: str | None = None


class FakeEvent(message.Event):
    """A simple mock event."""
    counter: int = 0

    @property
    def is_handled(self) -> bool:
        return self.counter > 0


class FakeCommandHandler(handler.CommandHandler[str | None]):
    """A simple handler for the mock command. The handler returns the
    command data."""

    def __init__(self, err: Exception | None = None) -> None:
        super().__init__()
        self.is_handled = False
        self._err = err

    def handle(self, cmd: FakeCommand) -> str | None:
        self.is_handled = True
        cmd.is_handled = True
        if self._err:
            raise self._err
        return cmd.data


class FakeEventHandler(handler.EventHandler):
    """A simple event handler for the mock event. The handler set the
    is_handled attribute of the event to True."""

    def __init__(self, err: Exception | None = None) -> None:
        super().__init__()
        self.is_handled = False
        self._err = err

    def handle(self, event: FakeEvent) -> None:
        self.is_handled = True
        event.counter += 1
        if self._err:
            raise self._err
        return self.next(event)
