import abc
import typing as t
from collections import defaultdict

from wemux import errors
from wemux import message
from wemux import middleware

T = t.TypeVar('T')
E = t.TypeVar('E')


class CommandHandler:
    """A command handler is a callable that takes a command and can optional
    returns a result."""

    @abc.abstractmethod
    def handle(self, command: message.Command) -> t.Any:
        """Call the command handler."""
        raise NotImplementedError


class EventListener:
    """An event listener is a callable that takes an event and returns
    nothing."""

    @abc.abstractmethod
    def handle(self, event: message.Event) -> None:
        """Call the event listener."""
        raise NotImplementedError


type CommandHandlerMap = t.Dict[t.Type[message.Command], CommandHandler]
"""A command handler map is a dictionary that maps a command to a command
handler."""

type CommandHandlerStrategyFunc = t.Callable[[
    CommandHandlerMap,
    message.Command
], t.Any]
"""The command handler strategy is a callable that takes a dictionary of
command handlers and a command. The callable returns the result of the
command handler."""

type EventHandlerStrategyFunc = t.Callable[[
    t.List[EventListener],
    message.Event
], None]
"""The event handler strategy is a callable that takes a list of event
listeners and an event. The callable returns nothing."""


class CommandHandlerStrategy(abc.ABC):

    @abc.abstractmethod
    def __call__(
        self,
        command_handlers: CommandHandlerMap,
        command: message.Command
    ) -> t.Any:
        raise NotImplementedError


class EventHandlerStrategy(abc.ABC):

    @abc.abstractmethod
    def __call__(
        self,
        event_listeners: list[EventListener],
        event: message.Event
    ) -> None:
        raise NotImplementedError


class LocalCommandHandlerStrategy(CommandHandlerStrategy):

    def __init__(self, middlewares: list[middleware.Middleware] | None = None) -> None:
        self._middlewares: list[middleware.Middleware] = middlewares or []

    def __call__(
        self,
        command_handlers: t.Dict[t.Type[message.Command], CommandHandler],
        command: message.Command
    ) -> t.Any:
        handler = command_handlers.get(type(command))
        if handler is None:
            raise errors.HandlerNotFoundError(
                f"no handler for command {command}")
        try:
            for _middleware in self._middlewares:
                _middleware.before(command)
            result = handler.handle(command)
            for _middleware in self._middlewares:
                _middleware.after(command)
            return result
        except Exception as ex:
            for _middleware in self._middlewares:
                _middleware.error(command, ex)
            raise ex


class LocalEventHandlerStrategy(EventHandlerStrategy):

    def __init__(self, middlewares: list[middleware.Middleware] | None = None) -> None:
        self._middlewares: list[middleware.Middleware] = middlewares or []

    def __call__(
        self,
        event_listeners: list[EventListener],
        event: message.Event
    ) -> None:
        for listener in event_listeners:
            try:
                for _middleware in self._middlewares:
                    _middleware.before(event)
                listener.handle(event)
                for _middleware in self._middlewares:
                    _middleware.after(event)
            except Exception as ex:
                for _middleware in self._middlewares:
                    _middleware.error(event, ex)


class MessageBus:
    """The message bus is the central point to send and receive messages.
    It is a simple pub/sub system. Messages are send to the bus and
    listeners are subscribed to the bus. Each message is send to each
    listener."""

    def __init__(
        self,
        command_strategy: CommandHandlerStrategyFunc,
        event_strategy: EventHandlerStrategyFunc
    ) -> None:
        self._command_strategy = command_strategy
        self._event_strategy = event_strategy
        self._command_handlers: t.Dict[
            t.Type[message.Command],
            CommandHandler
        ] = {}
        """The command handlers. Each command handler is called when a
        command is send to the bus."""
        self._event_listeners: t.Dict[
            t.Type[message.Event],
            t.List[EventListener]
        ] = defaultdict(list)
        """The event listeners. Each event listener is called when an
        event is send to the bus."""

    def add_listener(
        self,
        key: t.Type[message.Event],
        listener: EventListener
    ) -> None:
        """Add an event listener to the bus."""
        self._event_listeners[key].append(listener)

    def add_handler(
        self,
        key: t.Type[message.Command],
        handler: CommandHandler
    ) -> None:
        """Add a command handler to the bus."""
        self._command_handlers[key] = handler

    def register_handler(self, command: t.Type[message.Command]) -> t.Callable:
        """A decorator to register a command handler. The decorator takes the
        command as an argument to identify the command."""

        def decorator(
            handler: t.Type[CommandHandler]
        ) -> t.Type[CommandHandler]:
            self.add_handler(command, handler())
            return handler

        return decorator

    def emit(self, event: message.Event) -> None:
        """Handle an event. The event is sent to all event listeners. When an
        event listener raises an exception, the exception is caught and logged.
        The event is not send to the other listeners."""
        self._event_strategy(self._event_listeners[type(event)], event)

    def handle(self, command: message.Command) -> t.Any:
        """Handle a command. The command is sent to the command handler.

        Returns:
            The result of the command handler.

        Raises:
            errors.CommandHandlerNotFoundError: when no handler is found.
        """
        return self._command_strategy(self._command_handlers, command)
