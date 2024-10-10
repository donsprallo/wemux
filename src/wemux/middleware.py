import logging
import typing as t

from wemux import message


class Middleware:
    """A middleware is a class that can be used to intercept messages. The
    middleware can be used to implement cross-cutting concerns. The methods
    before, after and error are called at different points in the message
    handling process."""

    def before(self, msg: message.Message) -> None:
        """Call the middleware before the message is handled."""
        pass

    def after(self, msg: message.Message) -> None:
        """Call the middleware after the message is handled."""
        pass

    def error(self, msg: message.Message, ex: Exception) -> None:
        """Call the middleware when an exception is raised."""
        pass


class LoggerMiddleware(Middleware):
    """A simple middleware that logs messages."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        super().__init__()
        if logger is None:
            # Create default logger.
            logger = logging.getLogger(__name__)
        self._logger = logger

    @t.override
    def before(self, msg: message.Message) -> None:
        self._logger.info(f"handle {msg}")

    @t.override
    def after(self, msg: message.Message) -> None:
        self._logger.info(f"{msg} handled successfully.")

    @t.override
    def error(self, msg: message.Message, ex: Exception) -> None:
        self._logger.error(ex)
