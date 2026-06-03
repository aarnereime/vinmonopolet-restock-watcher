from pathlib import Path

import requests

from api import VinmonopoletClient
from telegram_notifier import TelegramNotifier
from storage import load_watchlist, load_state, save_state
from models import WineProfile
from diff import compare_states

DATA_DIR = Path("data")
WATCHLIST_PATH = DATA_DIR / Path("watchlist.json")
STATE_PATH = DATA_DIR / Path("state.json")


def main():
    client = VinmonopoletClient()
    # telegram_notifier = TelegramNotifier()  
    
    watchlist = load_watchlist(WATCHLIST_PATH)
    previous = load_state(STATE_PATH)
    
    new_state: dict[str, WineProfile] = {}
    for producer in watchlist:
        try:
            wines = client.fetch_wines(brand_code=producer.brand_code)
        except requests.RequestException as e:
            print(f"Skipping {producer.name}: {e}")
            continue
        for wine in wines:
            new_state[wine.code] = wine
            
    for k, v in new_state.items():
        print(k, ":", v)
            
    # First run to establishing baseline state to compare against
    if previous is None:
        save_state(STATE_PATH, content=new_state)
        return
        
    
    # events = compare_states(previous, new_state)
    # if events:
    #     pass
        # notifier.send_events(events)
        
    save_state(STATE_PATH, content=new_state)


if __name__ == "__main__":
    main()
