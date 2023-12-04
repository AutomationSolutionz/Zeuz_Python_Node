from enum import Enum, auto


class EventType(Enum):
    MouseMove = auto()
    MouseUp = auto()
    MouseDown = auto()
    MouseWheel = auto()
    KeyDown = auto()
    KeyUp = auto()


class EventData:
    """
    Event Data, mouse or keyboard

    event_type: EventType, type of event that occurred
    timestamp: str, time when event occurred
    data: object, data of event

    """

    def __init__(self, event_type: EventType, timestamp: str, data: object):
        self.event_type = event_type
        self.timestamp = timestamp
        self.data = data

    def __repr__(self) -> str:
        return f"{self.timestamp}: {self.event_type}, {self.data}"
