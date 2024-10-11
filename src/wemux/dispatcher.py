import abc
import typing as t

from wemux import errors
from wemux import handler
from wemux import message

type CommandHandlerMap = t.Dict[t.Type[message.Command], handler.CommandHandler]
"""A command handler map is a dictionary that maps a command type to a specific
command handler."""


class CommandDispatcher(abc.ABC):
    """The CommandDispatcher is an abstract class that dispatches commands to
    command handlers. A derivative class must implement the dispatch method."""

    @abc.abstractmethod
    def dispatch(
        self,
        handlers: CommandHandlerMap,
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
        handlers: list[handler.EventHandler],
        event: message.Event
    ) -> None:
        """Dispatch an event to a list of event listeners."""
        raise NotImplementedError


class InMemoryCommandDispatcher(CommandDispatcher):

    def dispatch(
        self,
        handlers: CommandHandlerMap,
        command: message.Command
    ) -> t.Any:
        _handler = handlers.get(type(command))
        if _handler is None:
            raise errors.HandlerNotFoundError(
                f"no handler for command {command}")
        try:
            return _handler.handle(command)
        except Exception as ex:
            _handler.error(command, ex)
            raise ex


class InMemoryEventDispatcher(EventDispatcher):

    def dispatch(
        self,
        handlers: list[handler.EventHandler],
        event: message.Event
    ) -> None:
        for _handler in handlers:
            try:
                _handler.handle(event)
            except Exception as ex:
                _handler.error(event, ex)
