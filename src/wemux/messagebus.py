import abc
import logging
import typing as t
from collections import defaultdict

import pydantic

from wemux import errors

logger = logging.getLogger(__name__)

T = t.TypeVar('T')
E = t.TypeVar('E')

Message = t.Union['Event', 'Command']


class Event(pydantic.BaseModel):
    """Event is the base class for message bus events. The class inherits from
    pydantic BaseModel. An event is something that has happened in the past.
    Multiple listeners can listen to an event."""
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Command(pydantic.BaseModel):
    """Command is the base class for message bus commands. The class inherits
    from pydantic BaseModel. A command is described by the fact that it is
    executed immediately and can return a result."""
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Result(pydantic.BaseModel):
    """Result is the base class for message bus command results. The
    class inherits from pydantic BaseModel."""
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class CommandHandler:
    """A command handler is a callable that takes a command and can optional
    returns a result."""

    @abc.abstractmethod
    def handle(self, command: Command) -> t.Any:
        """Call the command handler."""
        raise NotImplementedError


class EventListener:
    """An event listener is a callable that takes an event and returns
    nothing."""

    @abc.abstractmethod
    def handle(self, event: Event) -> None:
        """Call the event listener."""
        raise NotImplementedError


class Middleware:
    """A middleware is a class that can be used to intercept messages. The
    middleware can be used to implement cross-cutting concerns. The methods
    before, after and error are called at different points in the message
    handling process."""

    def before(self, message: Message) -> None:
        """Call the middleware before the message is handled."""
        pass

    def after(self, message: Message) -> None:
        """Call the middleware after the message is handled."""
        pass

    def error(self, message: Message, ex: Exception) -> None:
        """Call the middleware when an exception is raised."""
        pass


class LoggerMiddleware(Middleware):
    """A simple middleware that logs messages."""

    @t.override
    def before(self, message: Message) -> None:
        logger.info(f"handle {message}")

    @t.override
    def after(self, message: Message) -> None:
        logger.info(f"{message} handled successfully.")

    @t.override
    def error(self, message: Message, ex: Exception) -> None:
        logger.error(ex)


type CommandHandlerMap = t.Dict[t.Type[Command], CommandHandler]
"""A command handler map is a dictionary that maps a command to a command
handler."""

type CommandHandlerStrategyFunc = t.Callable[[
    CommandHandlerMap,
    Command
], t.Any]
"""The command handler strategy is a callable that takes a dictionary of
command handlers and a command. The callable returns the result of the
command handler."""

type EventHandlerStrategyFunc = t.Callable[[
    t.List[EventListener],
    Event
], None]
"""The event handler strategy is a callable that takes a list of event
listeners and an event. The callable returns nothing."""


class CommandHandlerStrategy(abc.ABC):

    @abc.abstractmethod
    def __call__(
        self,
        command_handlers: CommandHandlerMap,
        command: Command
    ) -> t.Any:
        raise NotImplementedError


class EventHandlerStrategy(abc.ABC):

    @abc.abstractmethod
    def __call__(
        self,
        event_listeners: list[EventListener],
        event: Event
    ) -> None:
        raise NotImplementedError


class LocalCommandHandlerStrategy(CommandHandlerStrategy):

    def __init__(self, middleware: list[Middleware] | None = None) -> None:
        self._middleware: list[Middleware] = middleware or []

    def __call__(
        self,
        command_handlers: t.Dict[t.Type[Command], CommandHandler],
        command: Command
    ) -> t.Any:
        handler = command_handlers.get(type(command))
        if handler is None:
            raise errors.HandlerNotFoundError(
                f"no handler for command {command}")
        try:
            for middleware in self._middleware:
                middleware.before(command)
            result = handler.handle(command)
            for middleware in self._middleware:
                middleware.after(command)
            return result
        except Exception as ex:
            for middleware in self._middleware:
                middleware.error(command, ex)
            raise ex


class LocalEventHandlerStrategy(EventHandlerStrategy):

    def __init__(self, middleware: list[Middleware] | None = None) -> None:
        self._middleware: list[Middleware] = middleware or []

    def __call__(
        self,
        event_listeners: list[EventListener],
        event: Event
    ) -> None:
        for listener in event_listeners:
            try:
                for middleware in self._middleware:
                    middleware.before(event)
                listener.handle(event)
                for middleware in self._middleware:
                    middleware.after(event)
            except Exception as ex:
                for middleware in self._middleware:
                    middleware.error(event, ex)


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
            t.Type[Command],
            CommandHandler
        ] = {}
        """The command handlers. Each command handler is called when a
        command is send to the bus."""
        self._event_listeners: t.Dict[
            t.Type[Event],
            t.List[EventListener]
        ] = defaultdict(list)
        """The event listeners. Each event listener is called when an
        event is send to the bus."""

    def add_listener(
        self,
        key: t.Type[Event],
        listener: EventListener
    ) -> None:
        """Add an event listener to the bus."""
        self._event_listeners[key].append(listener)

    def add_handler(
        self,
        key: t.Type[Command],
        handler: CommandHandler
    ) -> None:
        """Add a command handler to the bus."""
        self._command_handlers[key] = handler

    def register_handler(self, command: t.Type[Command]) -> t.Callable:
        """A decorator to register a command handler. The decorator takes the
        command as an argument to identify the command."""

        def decorator(
            handler: t.Type[CommandHandler]
        ) -> t.Type[CommandHandler]:
            self.add_handler(command, handler())
            return handler

        return decorator

    def emit(self, event: Event) -> None:
        """Handle an event. The event is sent to all event listeners. When an
        event listener raises an exception, the exception is caught and logged.
        The event is not send to the other listeners."""
        self._event_strategy(self._event_listeners[type(event)], event)

    def handle(self, command: Command) -> t.Any:
        """Handle a command. The command is sent to the command handler.

        Returns:
            The result of the command handler.

        Raises:
            errors.CommandHandlerNotFoundError: when no handler is found.
        """
        return self._command_strategy(self._command_handlers, command)