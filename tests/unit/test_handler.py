import logging

import pytest

from wemux import LoggerMiddleware
from .fakes import FakeCommand
from .fakes import FakeCommandHandler
from .fakes import FakeEvent
from .fakes import FakeEventHandler


class TestEventHandler:

    def test_single_handler_must_return_ok(self):
        _handler = FakeEventHandler()
        _event = FakeEvent()

        _handler.handle(_event)

        assert _handler.is_handled is True
        assert _event.is_handled is True

    def test_must_handle_multiple_handlers(self):
        _handler1 = FakeEventHandler()
        _handler2 = FakeEventHandler()
        _handler3 = FakeEventHandler()
        _event = FakeEvent()

        _handler = _handler1 \
            .chain(_handler2) \
            .chain(_handler3)
        _handler1.handle(_event)

        assert _handler1.is_handled is True
        assert _handler2.is_handled is True
        assert _handler3.is_handled is True
        assert _handler.is_handled is True
        assert _event.counter == 3

    def test_must_handle_error(self):
        _handler1 = FakeEventHandler()
        _handler2 = FakeEventHandler(err=Exception())
        _handler3 = FakeEventHandler()
        _event = FakeEvent()

        _handler = _handler1 \
            .chain(_handler2) \
            .chain(_handler3)
        with pytest.raises(Exception):
            _handler1.handle(_event)

        assert _handler1.is_handled is True
        assert _handler2.is_handled is False
        assert _handler3.is_handled is False
        assert _handler.is_handled is False
        assert _event.counter == 1


class TestCommandHandler:

    def test_handler_must_return_none(self):
        _handler = FakeCommandHandler()
        _command = FakeCommand()

        result = _handler.handle(_command)

        assert result is None
        assert _handler.is_handled is True
        assert _command.is_handled is True

    def test_handler_must_return_data(self):
        _handler = FakeCommandHandler()
        _command = FakeCommand(data="test")

        result = _handler.handle(_command)

        assert result == _command.data
        assert _handler.is_handled is True
        assert _command.is_handled is True

    def test_must_handle_error(self):
        _handler = FakeCommandHandler(err=Exception())
        _command = FakeCommand()

        with pytest.raises(Exception):
            _handler.handle(_command)

        assert _handler.is_handled is False
        assert _command.is_handled is False

    def test_can_chain_handler(self):
        _logger = logging.getLogger(__name__)
        _command = FakeCommand()

        _handler = LoggerMiddleware(_logger)
        _handler.chain(FakeCommandHandler())
        _handler.handle(_command)

        assert _command.is_handled is True
        assert _command.data is None
