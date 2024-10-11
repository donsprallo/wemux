import abc
import typing as t

from wemux import errors
from wemux import handler
from wemux import message
from wemux import middleware

type CommandHandlerMap = t.Dict[t.Type[message.Command], handler.CommandHandler]
"""A command handler map is a dictionary that maps a command type to a specific
command handler."""


class CommandDispatcher(abc.ABC):
    """The CommandDispatcher is an abstract class that dispatches commands to
    command handlers. A derivative class must implement the dispatch method."""

    @abc.abstractmethod
    def dispatch(
        self,
        command_handlers: CommandHandlerMap,
        command: message.Command
    ) -> t.Any:
        """Dispatch a command to a command handler."""
        raise NotImplementedError


class EventDispatcher(abc.ABC):
    """The EventDispatcher is an abstract class that dispatches events to event
    listeners. A derivative class must implement the dispatch method."""

    @abc.abstractmethod
    def dispatch(
        self,
        event_listeners: list[handler.EventListener],
        event: message.Event
    ) -> None:
        """Dispatch an event to a list of event listeners."""
        raise NotImplementedError


class InMemoryCommandDispatcher(CommandDispatcher):

    def __init__(self, middlewares: list[middleware.Middleware] | None = None) -> None:
        self._middlewares: list[middleware.Middleware] = middlewares or []

    def dispatch(
        self,
        command_handlers: CommandHandlerMap,
        command: message.Command
    ) -> t.Any:
        _handler = command_handlers.get(type(command))
        if _handler is None:
            raise errors.HandlerNotFoundError(
                f"no handler for command {command}")
        try:
            for _middleware in self._middlewares:
                _middleware.before(command)
            result = _handler.handle(command)
            for _middleware in self._middlewares:
                _middleware.after(command)
            return result
        except Exception as ex:
            for _middleware in self._middlewares:
                _middleware.error(command, ex)
            raise ex


class InMemoryEventDispatcher(EventDispatcher):

    def __init__(self, middlewares: list[middleware.Middleware] | None = None) -> None:
        self._middlewares: list[middleware.Middleware] = middlewares or []

    def dispatch(
        self,
        event_listeners: list[handler.EventListener],
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
