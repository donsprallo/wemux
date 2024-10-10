class MessageBusError(Exception):
    """The base class for all message bus errors."""
    pass


class CommandHandlerNotFoundError(MessageBusError):
    """Raised when no command handler is found for a command."""
    pass
