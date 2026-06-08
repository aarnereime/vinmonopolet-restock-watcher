import json
from pathlib import Path
from dataclasses import asdict

from models import Availability, Producer, StoreStockLevel, WineProfile


def load_watchlist(path: Path) -> list[Producer]:
    watchlist_data = json.loads(path.read_text())
    return [Producer(**p) for p in watchlist_data["producers"]]


def _wine_from_dict(wine: dict) -> WineProfile:
    available = dict(wine["available"])
    stores = available.get("stores")
    if stores is not None:
        available["stores"] = [StoreStockLevel(**store) for store in stores]
    return WineProfile(**{**wine, "available": Availability(**available)})


def load_state(path: Path) -> dict[str, WineProfile] | None:
    if not path.exists():
        return None
    raw = json.loads(path.read_text())
    return {code: _wine_from_dict(wine) for code, wine in raw.items()}


def save_state(path: Path, content: dict[str, WineProfile]):
    serializable = {code: asdict(wineprofile) for code, wineprofile in content.items()}
    path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False)) 
    