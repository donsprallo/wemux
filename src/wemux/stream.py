import abc
import typing as t

from wemux import message


class EventStreamReader(abc.ABC):

    @abc.abstractmethod
    def read_events(self) -> t.Sequence[message.Event]:
        raise NotImplementedError


class EventStream(t.Iterator[message.Event]):

    def __init__(self, stream_reader: EventStreamReader) -> None:
        self._stream_reader = stream_reader
        self._events: list[message.Event] = []

    def add(self, event: message.Event) -> None:
        self._events.append(event)

    def __iter__(self) -> t.Self:
        return self

    def __next__(self) -> message.Event:
        if not self._events:
            raise StopIteration
        # Collect events from the collector.
        for event in self._stream_reader.read_events():
            self._events.append(event)
        # return the first event.
        return self._events.pop(0)


class InMemoryEventStreamReader(EventStreamReader):

    def read_events(self) -> t.Sequence[message.Event]:
        return []
