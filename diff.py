from dataclasses import dataclass

from models import WineProfile


@dataclass
class RestockEvent:
    wine: WineProfile
    event_type: str


def compare_states(
    previous: dict[str, WineProfile],
    current: dict[str, WineProfile],
) -> list[RestockEvent]:
    
    # TODO: finish the logic here
    
    events = []
    for code, wine in current.items():
        if not wine.available:
            continue
        prev = previous.get(code)
        if prev is None:
            events.append(RestockEvent(wine=wine, event_type="new_listing"))
        elif not prev.available:
            events.append(RestockEvent(wine=wine, event_type="restock"))
    return events