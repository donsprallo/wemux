import abc
import typing as t

from wemux import message


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
