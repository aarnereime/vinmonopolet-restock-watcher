import html
import os

import requests
from diff import RestockEvent, EventTypes
from models import Availability, WineProfile
from dotenv import load_dotenv

load_dotenv()

TOP_STORES = 5


class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.timeout = 10


    def send(self, text: str, *, parse_mode: str = "HTML", disable_web_page_preview: bool = True) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        r = requests.post(url, data=payload, timeout=self.timeout)
        r.raise_for_status()


    # def check_get_updates_endpoint(self) -> dict:
    #     url = f"https://api.telegram.org/bot{self.token}/getUpdates?limit=1"
    #     r = requests.get(url, timeout=self.timeout)
    #     r.raise_for_status()
    #     return r.json()
    
    
    def send_events(self, events: list[RestockEvent]) -> None:
        if not events:
            return

        sections: list[str] = []
        for event_type, header in (
            (EventTypes.NEW_LISTING, "🆕 <b>New listings</b>"),
            (EventTypes.RESTOCK, "🔄 <b>Restocks</b>"),
        ):
            wines = [e.wine for e in events if e.event_type is event_type]
            if not wines:
                continue
            lines = [header]
            for wine in wines:
                lines.append(self._format_wine(wine))
            sections.append("\n\n".join(lines))

        self.send("\n\n".join(sections))


    def _format_wine(self, wine: WineProfile) -> str:
        name = html.escape(wine.name)
        lines = [f'<a href="{wine.url}">{name}</a>']
        if wine.price is not None:
            lines.append(f"{wine.price:.2f} kr")

        lines.append(self._format_availability(wine.available))
        return "\n".join(lines)


    def _format_availability(self, availability: Availability) -> str:
        if availability.online:
            return "🌐 Available online"

        stores = availability.stores or []
        top = stores[:TOP_STORES]
        if not top:
            return "🏬 Available in stores"

        lines = ["🏬 Available in stores:"]
        for store in top:
            lines.append(
                f"• {html.escape(store.name)} - {store.distance_km:g} km ({store.stock} in stock)"
            )
        return "\n".join(lines)