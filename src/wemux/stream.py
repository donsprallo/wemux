import abc
import typing as t

from wemux import message


class EventStream(abc.ABC):
    """EventStream is an abstract class that reads events from a
    stream. A derivative class must implement the _read_events method.
    This method returns a sequence of events."""

    def __init__(self):
        """Create a new event stream."""
        self._events: list[message.Event] = []

    def __iter__(self) -> t.Self:
        """Return the event stream iterator."""
        return self

    def __next__(self) -> message.Event:
        """Return the next event from the stream."""
        if not self._events:
            raise StopIteration
        # Collect events from the collector.
        for event in self._read_events():
            self._events.append(event)
        # return the first event.
        return self._events.pop(0)

    def push_event(self, event: message.Event) -> None:
        """Push an event to the stream."""
        self._write_event(event)
        self._events.append(event)

    @abc.abstractmethod
    def _read_events(self) -> t.Sequence[message.Event]:
        """Read events from the stream. This method must be implemented by
        the derivative class. The returned sequence of events is empty if
        no events are available. Handled events are removed from the
        stream. Each event shall only return once."""
        raise NotImplementedError

    @abc.abstractmethod
    def _write_event(self, event: message.Event) -> None:
        """Write an event to the stream. This method must be implemented by
        the derivative class."""
        raise NotImplementedError


class InMemoryEventStream(EventStream):
    """InMemoryEventStreamReader reads events from an in-memory stream.
    There is no external system required. The stream is used when only
    internal communication is required."""

    @t.override
    def _read_events(self) -> t.Sequence[message.Event]:
        # Nothing to do here. The in-memory stream does not read events
        # from an external stream.
        return []

    @t.override
    def _write_event(self, event: message.Event) -> None:
        # Nothing to do here. The in-memory stream does not write events
        # to an external stream.
        pass
