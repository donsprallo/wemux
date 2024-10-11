import abc
import logging
import typing as t

from wemux import message

T = t.TypeVar('T')
K = t.TypeVar('K')


class Handler(abc.ABC, t.Generic[T, K]):
    """A middleware is a class that can be used to intercept messages. The
    middleware can be used to implement cross-cutting concerns."""

    def __init__(self):
        self._next: t.Optional['Handler'] = None
        """The next middleware in the chain. When no middleware is available,
        the attribute is None. In this case, the middleware ends here."""

    def chain(self, middleware: 'Handler') -> 'Handler':
        """Chain the middleware. This method returns the middleware that was
        passed to the method. This allows to chain multiple middlewares in a
        single line."""
        self._next = middleware
        return middleware

    def next(self, msg: T, ex: Exception | None = None) -> K:
        """Call the next middleware in the chain. When an exception is
        provided, the error method is called. Otherwise, the handle method
        is called. When no next middleware is available, the method does
        nothing."""
        if self._next is not None:
            if ex is not None:
                self._next.error(msg, ex)
            else:
                return self._next.handle(msg)

    def handle(self, msg: T) -> K:
        """Handle the message. This method is called in the chain."""
        return self.next(msg)

    def error(self, msg: T, ex: Exception) -> None:
        """Handle an error. This method is called in the chain when
        an error occurs with a message."""
        self.next(msg, ex)


class CommandHandler(Handler[message.Command, t.Any]):
    """A command handler is a callable that takes a command and can optional
    returns a result."""

    @abc.abstractmethod
    def handle(self, command: message.Command) -> t.Any:
        """Call the command handler."""
        raise NotImplementedError


class EventHandler(Handler[message.Event, None]):
    """An event listener is a callable that takes an event and returns
    nothing."""

    @abc.abstractmethod
    def handle(self, event: message.Event) -> None:
        """Call the event listener."""
        raise NotImplementedError


class LoggerHandler(Handler[message.Message, None]):
    """A simple middleware that logs messages."""

    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()
        self._logger = logger

    @t.override
    def handle(self, msg: message.Message) -> None:
        self._logger.info(f"handle {msg}")
        self.next(msg)

    @t.override
    def error(self, msg: message.Message, ex: Exception) -> None:
        self._logger.error(ex)
        self.next(msg, ex)
