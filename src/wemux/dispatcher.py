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
        command_handlers: CommandHandlerMap,
        command: message.Command
    ) -> t.Any:
        """Dispatch a command to a command handler."""
        raise NotImplementedError

    def error(self, command: message.Command, ex: Exception) -> None:
        """Handle an error."""
        pass


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

    def error(self, event: message.Event, ex: Exception) -> None:
        """Handle an error."""
        pass


class InMemoryCommandDispatcher(CommandDispatcher):

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
            return _handler.handle(command)
        except Exception as ex:
            self.error(command, ex)
            raise ex


class InMemoryEventDispatcher(EventDispatcher):

    def dispatch(
        self,
        event_listeners: list[handler.EventListener],
        event: message.Event
    ) -> None:
        for listener in event_listeners:
            try:
                listener.handle(event)
            except Exception as ex:
                self.error(event, ex)
