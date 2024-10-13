import abc
import logging
import typing as t

from wemux import message
from wemux import stream

HT = t.TypeVar('HT', bound='Handler')
ET = t.TypeVar('ET', bound=Exception)
MT = t.TypeVar('MT', bound=message.Message)
RT = t.TypeVar('RT')


class Handler(abc.ABC, t.Generic[MT, RT]):
    """A middleware is a class that can be used to intercept messages. The
    middleware can be used to implement cross-cutting concerns."""

    def __init__(self):
        self._next: t.Optional[t.Self] = None
        """The next handler in the chain. When no handler is available,
        the attribute is None. In this case, the handler ends here."""
        self._prev: t.Optional[t.Self] = None
        """The previous handler in the chain. When no handler is available,
        the attribute is None. In this case, the handler is the first
        handler in the chain."""

    def chain(self, handler: HT) -> HT:
        """Chain the middleware. This method returns the middleware that was
        passed to the method. This allows to chain multiple middlewares in a
        single line."""
        self._next = handler
        handler._prev = self
        return handler

    def next(self, msg: MT, ex: Exception | None = None) -> RT:
        """Call the next middleware in the chain. When an exception is
        provided, the error method is called. Otherwise, the handle method
        is called. When no next middleware is available, the method does
        nothing."""
        # The chain ends here.
        if self._next is None:
            return None
        # Call the next handler in the chain.
        if ex is not None:
            self._next.error(msg, ex)
        return self._next.handle(msg)

    def handle(self, msg: MT) -> RT:
        """Handle the message. This method is called in the chain."""
        # By default, the handler does nothing. The method is overridden
        # by the derivative class. At this point, the handler can call
        # the next handler in the chain.
        return self.next(msg)

    def error(self, msg: MT, ex: Exception) -> None:
        """Handle an error. This method is called in the chain when
        an error occurs with a message."""
        # By default, the handler does nothing. The method is overridden
        # by the derivative class. At this point, the handler can call
        # the next handler in the chain.
        self.next(msg, ex)


class CommandHandler(Handler[message.Command, RT]):
    """A command handler is a callable that takes a command and can optional
    returns a result."""

    def __init__(self, event_stream: stream.EventStream):
        super().__init__()
        self._event_stream = event_stream

    @property
    def event_stream(self) -> stream.EventStream:
        return self._event_stream

    @abc.abstractmethod
    def handle(self, cmd: message.Command) -> RT:
        """Call the command handler."""
        raise NotImplementedError


class EventHandler(Handler[message.Event, None]):
    """An event listener is a callable that takes an event and returns
    nothing."""

    def __init__(self, event_stream: stream.EventStream):
        super().__init__()
        self._event_stream = event_stream

    @property
    def event_stream(self) -> stream.EventStream:
        return self._event_stream

    @abc.abstractmethod
    def handle(self, event: message.Event) -> None:
        """Call the event listener."""
        raise NotImplementedError


class LoggerMiddleware(Handler[message.Message, None]):
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
