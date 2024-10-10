import abc
import typing as t

from wemux import errors
from wemux import handler
from wemux import message
from wemux import middleware

type CommandHandlerMap = t.Dict[t.Type[message.Command], handler.CommandHandler]
"""A command handler map is a dictionary that maps a command to a command
handler."""

type CommandDispatcherFunc = t.Callable[[
    CommandHandlerMap,
    message.Command
], t.Any]
"""The command dispatcher is a callable that takes a dictionary of
command handlers and a command. The callable returns the result of the
command handler."""

type EventDispatcherFunc = t.Callable[[
    t.List[handler.EventListener],
    message.Event
], None]
"""The event dispatcher is a callable that takes a list of event
listeners and an event. The callable returns nothing."""


class CommandDispatcher(abc.ABC):

    @abc.abstractmethod
    def dispatch(
        self,
        command_handlers: CommandHandlerMap,
        command: message.Command
    ) -> t.Any:
        raise NotImplementedError

    def __call__(
        self,
        command_handlers: CommandHandlerMap,
        command: message.Command
    ) -> t.Any:
        return self.dispatch(command_handlers, command)


class EventDispatcher(abc.ABC):

    @abc.abstractmethod
    def dispatch(
        self,
        event_listeners: list[handler.EventListener],
        event: message.Event
    ) -> None:
        raise NotImplementedError

    def __call__(
        self,
        event_listeners: list[handler.EventListener],
        event: message.Event
    ) -> None:
        self.dispatch(event_listeners, event)


class LocalCommandDispatcher(CommandDispatcher):

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


class LocalEventDispatcher(EventDispatcher):

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
