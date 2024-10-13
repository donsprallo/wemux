import typing as t

import pydantic

T = t.TypeVar('T')
E = t.TypeVar('E')


class Event(pydantic.BaseModel):
    """Event is the base class for message bus events. The class inherits from
    pydantic BaseModel. An event is something that has happened in the past.
    Multiple listeners can listen to an event."""
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Command(pydantic.BaseModel):
    """Command is the base class for message bus commands. The class inherits
    from pydantic BaseModel. A command is described by the fact that it is
    executed immediately and can return a result."""
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


Message = t.Union['Event', 'Command']
"""A message is either an event or a command."""
