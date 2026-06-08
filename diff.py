from dataclasses import dataclass
from enum import Enum

from models import WineProfile


class EventTypes(str, Enum):
    NEW_LISTING = "new_listing"
    RESTOCK = "restock"

@dataclass
class RestockEvent:
    wine: WineProfile
    event_type: EventTypes


def compare_states(
    previous: dict[str, WineProfile],
    current: dict[str, WineProfile],
) -> list[RestockEvent]:
    events: list[RestockEvent] = []

    for code, wine in current.items():
        prev = previous.get(code)

        if prev is None:
            events.append(RestockEvent(wine=wine, event_type=EventTypes.NEW_LISTING))
            continue

        if not prev.available.is_available and wine.available.is_available:
            events.append(RestockEvent(wine=wine, event_type=EventTypes.RESTOCK))

    return events