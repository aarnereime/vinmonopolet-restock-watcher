import requests

from models import WineProfile


class VinmonopoletClient:
    SEARCH_URL = "https://www.vinmonopolet.no/vmpws/v2/vmp/products/search"
    PRODUCT_URL_BASE = "https://www.vinmonopolet.no"
    DEFAULT_USER_AGENT = "vinmonopolet-restock-watcher/0.1 (personal project)"

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT, timeout: float = 15.0):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "application/json",
            }
        )


    def fetch_wines(self, brand_code: str) -> list[WineProfile]:
        return [
            self._parse(p, brand_code)
            for p in self._fetch_all_wines_by_brand(brand_code)
        ]


    def _fetch_all_wines_by_brand(self, brand_code: str) -> list[dict]:
        first_response = self._search(brand_code, page=0)
        
        products: list[dict] = first_response["products"]
        pagination = int(first_response["pagination"]["totalPages"])
        
        for page in range(1, pagination):
            next_page_response = self._search(brand_code, page=page)
            products.extend(next_page_response["products"])

        return products


    def _search(self, brand_code: str, page: int, page_size: int = 50) -> dict:
        params = {
            "fields": "FULL",
            "pageSize": page_size,
            "currentPage": page,
            "q": f":name-asc:brand:{brand_code}",
        }
        r = self.session.get(self.SEARCH_URL, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    
    def _determine_availability(self):
        return False


    def _parse(self, product: dict, brand_code: str) -> WineProfile:
        return WineProfile(
            code=product["code"],
            name=product["name"],
            brand_code=brand_code,
            available=self._determine_availability(),
            price=product["price"]["value"],
            url=f"{self.PRODUCT_URL_BASE}{product["url"]}"
        )
