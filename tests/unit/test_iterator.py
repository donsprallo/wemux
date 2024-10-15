import pytest

from wemux import iterator
from .fakes import FakeEvent


class TestInMemoryEventIterator:

    def test_can_push_event(self):
        _stream = iterator.InMemoryEventIterator()
        _event = FakeEvent()
        _stream.push_event(_event)
        # The pushed event is stored in the stream. The stream is not
        # empty after the event is pushed. The event is not read from
        # the stream.
        assert _stream._events == [_event]
        assert _stream._read_events() == []

    def test_can_push_multiple_events(self):
        _stream = iterator.InMemoryEventIterator()
        _event1 = FakeEvent()
        _event2 = FakeEvent()
        _stream.push_event(_event1)
        _stream.push_event(_event2)
        # The pushed events are stored in the stream. The stream is not
        # empty after the events are pushed. The events are not read from
        # the stream.
        assert _stream._events == [_event1, _event2]
        assert _stream._read_events() == []

    def test_can_iterate_over_events(self):
        _stream = iterator.InMemoryEventIterator()
        _event = FakeEvent()
        _stream.push_event(_event)
        # Read the event from the stream. The event is removed from
        # the stream. The stream is empty after the event is read.
        assert next(_stream) == _event
        with pytest.raises(StopIteration):
            next(_stream)

    def test_can_read_event_without_error(self):
        _stream = iterator.InMemoryEventIterator()
        # Read does not do anything.
        assert _stream._events == []
        assert _stream._read_events() == []

    def test_can_write_event_without_error(self):
        _stream = iterator.InMemoryEventIterator()
        _event = FakeEvent()
        _stream._write_event(_event)
        # Write does not do anything.
        assert _stream._events == []
        assert _stream._read_events() == []

    def test_can_add_event_while_iteration(self):
        _stream = iterator.InMemoryEventIterator()
        _event1 = FakeEvent()
        _event2 = FakeEvent()
        _stream.push_event(_event1)
        # Read the first event from the stream. After the event is read,
        # the stream is empty.
        assert _stream._events == [_event1]
        assert next(_stream) == _event1
        assert _stream._events == []
        # Next we add a second event to the stream. The second event is
        # read from the stream. The stream is empty after the second event
        # is read.
        _stream.push_event(_event2)
        assert _stream._events == [_event2]
        assert next(_stream) == _event2
        with pytest.raises(StopIteration):
            next(_stream)
