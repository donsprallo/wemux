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
        command_dispatcher: dispatcher.CommandDispatcherFunc,
        event_dispatcher: dispatcher.EventDispatcherFunc,
        stream_reader: stream.EventStreamReader
    ) -> None:
        self._command_dispatcher = command_dispatcher
        self._event_dispatcher = event_dispatcher
        self._event_stream = stream. \
            EventStream(stream_reader)
        self._command_handlers: t.Dict[
            t.Type[message.Command],
            handler.CommandHandler
        ] = {}
        """The command handlers. Each command handler is called when a
        command is send to the bus."""
        self._event_listeners: t.Dict[
            t.Type[message.Event],
            t.List[handler.EventListener]
        ] = defaultdict(list)
        """The event listeners. Each event listener is called when an
        event is send to the bus."""

    def add_listener(
        self,
        key: t.Type[message.Event],
        listener: handler.EventListener
    ) -> None:
        """Add an event listener to the bus."""
        self._event_listeners[key].append(listener)

    def add_handler(
        self,
        key: t.Type[message.Command],
        hdl: handler.CommandHandler
    ) -> None:
        """Add a command handler to the bus."""
        self._command_handlers[key] = hdl

    def register_handler(self, command: t.Type[message.Command]) -> t.Callable:
        """A decorator to register a command handler. The decorator takes the
        command as an argument to identify the command."""

        def decorator(
            hdl: t.Type[handler.CommandHandler]
        ) -> t.Type[handler.CommandHandler]:
            self.add_handler(command, hdl())
            return hdl

        return decorator

    def emit(self, event: message.Event) -> None:
        """Handle an event. The event is sent to all event listeners. When an
        event listener raises an exception, the exception is caught and logged.
        The event is not send to the other listeners."""
        self._event_stream.add(event)
        self._emit_events()

    def handle(self, command: message.Command) -> t.Any:
        """Handle a command. The command is sent to the command handler.

        Returns:
            The result of the command handler.

        Raises:
            errors.CommandHandlerNotFoundError: when no handler is found.
        """
        result = self._command_dispatcher(self._command_handlers, command)
        self._emit_events()
        return result

    def _emit_events(self) -> None:
        for _event in self._event_stream:
            event_listener = self._event_listeners[type(_event)]
            self._event_dispatcher(event_listener, _event)
