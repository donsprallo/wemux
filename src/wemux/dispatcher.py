import typing as t

from wemux import errors
from wemux import handler
from wemux import message

CommandHandlerMap: t.TypeAlias = t.Dict[t.Type[message.Command], handler.CommandHandler]
"""A command handler map is a dictionary that maps a command type to a specific
command handler."""


class CommandDispatcher:
    """The CommandDispatcher is a class that dispatches commands to
    command handlers. It is required to register command handlers before
    dispatching commands. Each command handler is responsible for handling
    a specific command type. It is not possible to dispatch a command
    without a registered command handler."""

    @staticmethod
    def dispatch(
        handlers: CommandHandlerMap,
        command: message.Command
    ) -> t.Any:
        """Dispatch a command to a command handler.

        Args:
            handlers: The command handler map.
            command: The command to dispatch.

        Raises:
            errors.HandlerNotFoundError: when no handler is found.

        Returns:
            The result of the command handler.
        """
        _handler = handlers.get(type(command))
        if _handler is None:
            raise errors.HandlerNotFoundError(
                f"no handler for command {command}")
        try:
            return _handler.handle(command)
        except Exception as ex:
            _handler.error(command, ex)
            raise ex


class EventDispatcher:
    """The EventDispatcher is a class that dispatches events to event
    handlers. It is not required to register event handlers before dispatching
    events. Each event handler is responsible for handling a specific event
    type. It is possible to dispatch an event without a registered event."""

    @staticmethod
    def dispatch(
        handlers: list[handler.EventHandler],
        event: message.Event
    ) -> None:
        """Dispatch an event to a list of event handlers.

        Args:
            handlers: The event handlers.
            event: The event to dispatch.
        """
        for _handler in handlers:
            try:
                _handler.handle(event)
            except Exception as ex:
                _handler.error(event, ex)
