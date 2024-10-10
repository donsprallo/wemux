class MessageBusError(Exception):
    """The base class for all message bus errors."""
    pass


class HandlerNotFoundError(MessageBusError):
    """Raised when no handler is found for a command or a message."""
    pass
