from wemux import handler
from wemux import iterator
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
    """A simple handler for the mock command. Normally the handler returns the
    fake command data."""

    def __init__(
        self,
        stream: handler.EventStream | None = None,
        events: list[message.Event] | None = None,
        err: Exception | None = None
    ) -> None:
        super().__init__(stream or iterator.InMemoryEventIterator())
        self.is_handled = False
        self._events = events or []
        self._err = err

    def handle(self, cmd: FakeCommand) -> str | None:
        if self._err:
            # Simulate an error.
            raise self._err
        # Simulate that the command handler has
        # handled the command and the handler.
        self.is_handled = True
        cmd.is_handled = True
        if self._events:
            # Simulate that the command handler push
            # events to the event stream.
            for _event in self._events:
                self.push(_event)
        return cmd.data


class FakeEventHandler(handler.EventHandler):
    """A simple event handler for the mock event. The handler set the
    is_handled attribute of the event to True."""

    def __init__(
        self,
        stream: handler.EventStream | None = None,
        events: list[message.Event] | None = None,
        err: Exception | None = None
    ) -> None:
        if stream is None:
            stream = iterator \
                .InMemoryEventIterator()
        super().__init__(stream)
        self.is_handled = False
        self._events = events or []
        self._err = err

    def handle(self, event: FakeEvent) -> None:
        if self._err:
            # Simulate an error.
            raise self._err
        # Simulate that the event handler has
        # handled the event and the handler.
        self.is_handled = True
        event.counter += 1
        if self._events:
            # Simulate that the event handler push
            # events to the event stream.
            for _event in self._events:
                # Protect against infinite loops.
                if _event.is_handled:
                    continue
                self.push(_event)
        return self.next(event)
