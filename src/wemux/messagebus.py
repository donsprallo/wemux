import typing as t
from collections import defaultdict

from wemux import dispatcher
from wemux import handler
from wemux import iterator
from wemux import message


class MessageBus:
    """The message bus is the central point to send and receive messages.
    It is a simple pub/sub system. Messages are send to the bus and
    listeners are subscribed to the bus. Each message is send to each
    listener."""

    def __init__(
        self,
        command_dispatcher: dispatcher.CommandDispatcher,
        event_dispatcher: dispatcher.EventDispatcher,
        event_iterator: iterator.EventIterator
    ) -> None:
        self._command_dispatcher = command_dispatcher
        self._event_dispatcher = event_dispatcher
        self._event_iterator = event_iterator
        self._command_handlers: t.Dict[
            type[message.Command],
            handler.CommandHandler
        ] = {}
        """The command handlers. Each command handler is called when a
        command is send to the bus."""
        self._event_handlers: t.Dict[
            type[message.Event],
            list[handler.EventHandler]
        ] = defaultdict(list)
        """The event handlers. Each event handler is called when an
        event is send to the bus."""

    @property
    def events(self) -> iterator.EventIterator:
        """Return the event stream."""
        return self._event_iterator

    def subscribe_event(
        self,
        key: type[message.Event],
        hdl: handler.EventHandler
    ) -> None:
        """Add an event handler to the bus."""
        self._event_handlers[key].append(hdl)

    def subscribe_command(
        self,
        key: type[message.Command],
        hdl: handler.CommandHandler
    ) -> None:
        """Add a command handler to the bus."""
        self._command_handlers[key] = hdl

    def subscribe(
        self,
        command: type[message.Message],
        *args: t.Any,
        **kwargs: t.Any
    ) -> t.Callable:
        """A decorator to register a command handler. The decorator takes the
        command as an argument for identification. The decorator can take
        additional arguments that are passed to the handler constructor.

        Args:
            command: The command to handle.
            args: Additional arguments for the handler constructor.
            kwargs: Additional keyword arguments for the handler constructor.

        Returns:
            A decorator that registers the handler to the bus.
        """
        kwargs.setdefault('stream', self.events)
        middleware = kwargs.pop('middleware', None)

        def decorator(
            hdl: type[handler.Handler]
        ) -> type[handler.Handler]:
            _handler = hdl(*args, **kwargs) # noqa
            # Register the handler to the bus.
            if isinstance(_handler, handler.CommandHandler):
                self.subscribe_command(command, _handler)
            elif isinstance(_handler, handler.EventHandler):
                self.subscribe_event(command, _handler)
            else:
                raise ValueError("handler must be a CommandHandler "
                                 "or EventHandler")
            # Add middleware to the handler chain.
            if isinstance(middleware, handler.Handler):
                _handler.chain(middleware)
            return hdl

        return decorator

    def emit(self, event: message.Event) -> None:
        """Handle an event. The event is sent to all event handlers. When an
        event handler raises an exception, the exception is caught and the
        execution goes to the next event handlers.

        Args:
            event: The event to handle.
        """
        self._event_iterator.push_event(event)
        self._emit_events()

    def handle(self, command: message.Command) -> t.Any:
        """Handle a command. The command is sent to the command handler. When
        the command handler raises an exception, the handler error method is
        called. After that, the exception is re-raised.

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
        """Emit events to the event handlers."""
        for _event in self._event_iterator:
            _handlers = self._event_handlers[type(_event)]
            self._event_dispatcher.dispatch(
                _handlers, _event)


def create_in_memory_message_bus() -> MessageBus:
    """Create an in memory message bus."""
    return MessageBus(
        dispatcher.CommandDispatcher(),
        dispatcher.EventDispatcher(),
        iterator.InMemoryEventIterator()
    )
