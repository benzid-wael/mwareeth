from enum import Enum
from typing import Type

from statemachine import Event

EnumType = Type[Enum]


class Events:
    """
    A class representing a collection of Event objects.

    Helps creating :ref:`StateMachine`'s :ref:`event` definitions from other
    sources, like an ``Enum`` class, using :meth:`Events.from_enum`.
    """

    def __init__(self, events: dict[str, Event] | None = None) -> None:
        self._events: dict[str, Event] = events or {}

    @classmethod
    def from_enum(cls, enum_type: EnumType):
        """
        Creates a new instance of the ``Events`` class from an enumeration.
        """
        return cls({e.name: Event(id=e.name, name=e.name) for e in enum_type})

    def append(self, event: Event):
        self._events[event.name] = event

    def items(self):
        """
        Returns a view object of the events, with pairs of ``(Event.id, Event)``.
        """
        return self._events.items()

    def __repr__(self):
        return f"{list(self)}"

    def __eq__(self, other):
        return list(self) == list(other)

    def __getattr__(self, name: str):
        if name in self._events:
            return self._events[name]
        raise AttributeError(f"{name} not found in {self.__class__.__name__}")

    def __len__(self):
        return len(self._events)

    def __iter__(self):
        return iter(self._events.values())
