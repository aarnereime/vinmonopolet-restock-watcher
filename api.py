import json
import requests

from models import WineProfile


BRYNE_STORE_LOCATION = {
   "latitude" : 58.735793,
   "longitude" : 5.6477347
}


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
        # print("kekek")
        # print(json.dumps(first_response, indent = 4))

        products = list(first_response["products"])
        total_pages = first_response["pagination"]["totalPages"]

        for page in range(1, total_pages):
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

    def _determine_store_availability(self, wine_code: str):
        lat = BRYNE_STORE_LOCATION["latitude"]
        lon = BRYNE_STORE_LOCATION["longitude"]
        url = f"https://www.vinmonopolet.no/vmpws/v2/vmp/products/{wine_code}/stock?pageSize=10&currentPage=0&fields=BASIC&latitude={lat}&longitude={lon}"
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _determine_availability(self, availability_info: dict, wine_code: str):
        print(availability_info)
        if availability_info["deliveryAvailability"]["availableForPurchase"]:
            return True
        
        # determine if available in stores if delivery is not available
        if availability_info["storesAvailability"]["availableForPurchase"]:
            res = self._determine_store_availability(wine_code)
            # res["pointOfService"]
            # - "formattedDistance" : "575,7 km"
            # res["stockInfo"]["stockLevel"]
            if res["stores"]: return True
            # for store in res["stores"]:
            # To easily determine if it actaully avaiable just check that the distance is inside a certain range, because then its actaully possible to buy and retrieve
            
        return False
    

    def _parse(self, product: list[dict], brand_code: str) -> WineProfile:
        return WineProfile(
            code=product["code"],
            name=product["name"],
            brand_code=brand_code,
            available=self._determine_availability(product["productAvailability"], product["code"]),
            price=product["price"]["value"],
            url=f"{self.PRODUCT_URL_BASE}{product['url']}",
        )
