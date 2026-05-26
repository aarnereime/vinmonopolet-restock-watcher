import json
from pathlib import Path
from dataclasses import asdict

from models import Producer, WineProfile


def load_watchlist(path: Path) -> list[Producer]:
    watchlist_data = json.loads(path.read_text())
    return [Producer(**p) for p in watchlist_data["producers"]]
    
    
def load_state(path: Path) -> dict[str, WineProfile]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    return {code: WineProfile(**wine) for code, wine in raw.items()}


def save_state(path: Path, content: dict[str, WineProfile]):
    serializable = {code: asdict(wineprofile) for code, wineprofile in content.items()}
    path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False)) 
    