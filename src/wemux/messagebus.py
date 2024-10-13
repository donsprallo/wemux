import typing as t
from collections import defaultdict

from wemux import dispatcher
from wemux import handler
from wemux import message
from wemux import stream


class MessageBus:
    """The message bus is the central point to send and receive messages.
    It is a simple pub/sub system. Messages are send to the bus and
    listeners are subscribed to the bus. Each message is send to each
    listener."""

    def __init__(
        self,
        command_dispatcher: dispatcher.CommandDispatcher,
        event_dispatcher: dispatcher.EventDispatcher,
        event_stream: stream.EventStream
    ) -> None:
        self._command_dispatcher = command_dispatcher
        self._event_dispatcher = event_dispatcher
        self._event_stream = event_stream
        self._command_handlers: t.Dict[
            t.Type[message.Command],
            handler.CommandHandler
        ] = {}
        """The command handlers. Each command handler is called when a
        command is send to the bus."""
        self._event_handlers: t.Dict[
            t.Type[message.Event],
            t.List[handler.EventHandler]
        ] = defaultdict(list)
        """The event handlers. Each event handler is called when an
        event is send to the bus."""

    @property
    def event_stream(self) -> stream.EventStream:
        """Return the event stream."""
        return self._event_stream

    def register_event_handler(
        self,
        key: t.Type[message.Event],
        hdl: handler.EventHandler
    ) -> None:
        """Add an event handler to the bus."""
        self._event_handlers[key].append(hdl)

    def register_command_handler(
        self,
        key: t.Type[message.Command],
        hdl: handler.CommandHandler
    ) -> None:
        """Add a command handler to the bus."""
        self._command_handlers[key] = hdl

    def register_handler(
        self,
        command: t.Type[message.Message],
        *args: t.Any,
        **kwargs: t.Any
    ) -> t.Callable:
        """A decorator to register a command handler. The decorator takes the
        command as an argument to identify the command."""
        kwargs.setdefault("event_stream", self.event_stream)

        def decorator(
            hdl: t.Type[handler.Handler]
        ) -> t.Type[handler.Handler]:
            if issubclass(hdl, handler.CommandHandler):
                self.register_command_handler(
                    command, hdl(*args, **kwargs))  # noqa
            elif issubclass(hdl, handler.EventHandler):
                self.register_event_handler(
                    command, hdl(*args, **kwargs))  # noqa
            else:
                raise ValueError("handler must be a CommandHandler "
                                 "or EventHandler")
            return hdl

        return decorator

    def emit(self, event: message.Event) -> None:
        """Handle an event. The event is sent to all event listeners. When an
        event listener raises an exception, the exception is caught and logged.
        The event is not send to the other listeners."""
        self._event_stream.push_event(event)
        self._emit_events()

    def handle(self, command: message.Command) -> t.Any:
        """Handle a command. The command is sent to the command handler.

        Returns:
            The result of the command handler.

        Raises:
            errors.CommandHandlerNotFoundError: when no handler is found.
        """
        result = self._command_dispatcher.dispatch(
            self._command_handlers, command)
        self._emit_events()
        return result

    def _emit_events(self) -> None:
        for _event in self._event_stream:
            _handlers = self._event_handlers[type(_event)]
            self._event_dispatcher.dispatch(
                _handlers, _event)


def create_in_memory_message_bus() -> MessageBus:
    """Create an in memory message bus."""
    return MessageBus(
        dispatcher.InMemoryCommandDispatcher(),
        dispatcher.InMemoryEventDispatcher(),
        stream.InMemoryEventStream()
    )
