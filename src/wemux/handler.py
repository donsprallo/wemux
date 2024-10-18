import abc
import typing as t

from wemux import message

HT = t.TypeVar('HT', bound='Handler')
ET = t.TypeVar('ET', bound=Exception)
MT = t.TypeVar('MT', bound=message.Message)
RT = t.TypeVar('RT')


class Handler(abc.ABC, t.Generic[MT, RT]):
    """Handler is an abstract class that implements the chain of responsibility
    pattern. A handler can be chained with other handlers. When a message is
    passed to the handler, the message is processed by the handler and then
    passed to the next handler in the chain. When an exception occurs, the
    error method is called. The error method can also pass the exception to
    the next handler in the chain."""

    def __init__(self):
        self._next: t.Optional['Handler'] = None
        """The next handler in the chain. When no handler is available,
        the attribute is None. In this case, the handler ends here."""
        self._prev: t.Optional['Handler'] = None
        """The previous handler in the chain. When no handler is available,
        the attribute is None. In this case, the handler is the first
        handler in the chain."""

    def chain(self, handler: HT) -> HT:
        """Chain the middleware. This method returns the middleware that was
        passed to the method. This allows to chain multiple middlewares in a
        single line.

        Args:
            handler: The handler to be added to the chain.

        Returns:
            The last handler in the chain.
        """
        self._next = handler
        handler._prev = self
        return handler

    def next(self, msg: MT, ex: Exception | None = None) -> RT:
        """Call the next handler in the chain. When an exception is
        provided, the error method is called. Otherwise, the handle method
        is called. When no next middleware is available, the method does
        nothing.

        Args:
            msg: The message to be processed.
            ex: An optional exception that occurred with the message.

        Returns:
            The result of the next handler in the chain or None.
        """
        # The chain ends here.
        if self._next is None:
            return None
        # Call the next handler in the chain.
        if ex is not None:
            self._next.error(msg, ex)
        return self._next.handle(msg)

    def handle(self, msg: MT) -> RT:
        """Handle the message. This method is called in the chain.

        Args:
            msg: The message to be processed.

        Returns:
            The result of the handler.
        """
        # By default, the handler does nothing. The method is overridden
        # by the derivative class. At this point, the handler can call
        # the next handler in the chain.
        return self.next(msg)

    def error(self, msg: MT, ex: Exception) -> None:
        """Handle an error. This method is called in the chain when
        an error occurs with a message.

        Args:
            msg: The message to be processed.
            ex: The exception that occurred with the message.
        """
        # By default, the handler does nothing. The method is overridden
        # by the derivative class. At this point, the handler can call
        # the next handler in the chain.
        self.next(msg, ex)


class EventStream(t.Protocol):
    """An event stream is a simple interface to push events to the event
    stream. The interface can be implemented by different event stream
    implementations."""

    def push_event(self, event: message.Event) -> None:
        """Push an event to the event stream."""
        ...


class CommandHandler(Handler[message.Command, RT]):
    """CommandHandler is an abstract class that implements the Handler
    class with a specialization for commands. A derivative class must
    implement the handle method. A command handler can push events to
    the event stream. At command handling, the command handler can return
    a result."""

    def __init__(self, stream: EventStream):
        """Create a new command handler.

        Args:
            stream: The event iterator to push events.
        """
        super().__init__()
        self._stream = stream

    def push(self, event: message.Event) -> None:
        """Push an event to the event stream."""
        return self._stream.push_event(event)


class EventHandler(Handler[message.Event, None]):
    """EventHandler is an abstract class that implements the Handler class
    with a specialization for events. A derivative class must implement the
    handle method. An event handler can push events to the event stream.
    An event handler does not return a result."""

    def __init__(self, stream: EventStream):
        """Create a new event handler.

        Args:
            stream: The event iterator to push events.
        """
        super().__init__()
        self._event_iterator = stream

    def push(self, event: message.Event) -> None:
        """Push an event to the event stream."""
        return self._event_iterator.push_event(event)


class Logger(t.Protocol):
    """A simple logger interface. The interface defines the methods
    to log messages. The interface can be implemented by different
    logging libraries."""

    def info(self, msg, *args, **kwargs) -> None:
        ...

    def error(self, msg, *args, **kwargs) -> None:
        ...


class LoggerMiddleware(Handler[message.Message, None]):
    """A simple middleware that logs messages. Can be used for debugging
    purposes. The middleware logs the message and passes it to the next
    handler in the chain. It is usable for both commands and events."""

    def __init__(self, logger: Logger) -> None:
        """Create a new logger middleware.

        Args:
            logger: The logger to log messages.
        """
        super().__init__()
        self._logger = logger

    def handle(self, msg: message.Message) -> None:
        self._logger.info(f"handle {msg}")
        self.next(msg)

    def error(self, msg: message.Message, ex: Exception) -> None:
        self._logger.error(ex)
        self.next(msg, ex)
