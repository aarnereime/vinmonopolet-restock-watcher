import os

import requests
from dotenv import load_dotenv

load_dotenv()


class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.timeout = 10

    def send(self, text: str, *, parse_mode: str = "HTML", disable_web_page_preview: bool = False) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        r = requests.post(url, data=payload, timeout=self.timeout)
        r.raise_for_status()

    def check_get_updates_endpoint(self) -> dict:
        url = f"https://api.telegram.org/bot{self.token}/getUpdates?limit=1"
        r = requests.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()