import abc
import logging
import typing as t

from wemux import message


class Middleware(abc.ABC):
    """A middleware is a class that can be used to intercept messages. The
    middleware can be used to implement cross-cutting concerns."""

    def __init__(self):
        self._next: t.Optional['Middleware'] = None
        """The next middleware in the chain. When no middleware is available,
        the attribute is None. In this case, the middleware ends here."""

    def chain(self, middleware: 'Middleware') -> 'Middleware':
        """Chain the middleware. This method returns the middleware that was
        passed to the method. This allows to chain multiple middlewares in a
        single line."""
        self._next = middleware
        return middleware

    def next(
        self,
        msg: message.Message,
        ex: Exception | None = None
    ) -> None:
        """Call the next middleware in the chain. When an exception is
        provided, the error method is called. Otherwise, the handle method
        is called. When no next middleware is available, the method does
        nothing."""
        if self._next is not None:
            if ex is not None:
                self._next.error(msg, ex)
            else:
                self._next.handle(msg)

    def handle(self, msg: message.Message) -> None:
        """Handle the message. This method is called in the chain."""
        self.next(msg)

    def error(self, msg: message.Message, ex: Exception) -> None:
        """Handle an error. This method is called in the chain when
        an error occurs with a message."""
        self.next(msg, ex)


class LoggerMiddleware(Middleware):
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
