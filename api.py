import json
import requests

from models import WineProfile, Availability, StoreStockLevel
from collections import namedtuple


Location = namedtuple("Location", ["latitude", "longitude"])


STORE_LOCATIONS = {
    "Bryne": Location(latitude=58.735793, longitude=5.6477347)
}


class VinmonopoletClient:
    BASE_URL = "https://www.vinmonopolet.no"
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
        
    def _find_stores_with_wine_in_stock(self, wine_code: str):
        loc = STORE_LOCATIONS["Bryne"] # later it should be a parameter for the individual user
        
        store_stock_url = f"{self.BASE_URL}/vmpws/v2/vmp/products/{wine_code}/stock"
        params = {
            "pageSize": "10",
            "currentPage": "0",
            "fields": "BASIC",
            "latitude": loc.latitude,
            "longitude": loc.longitude
        }
        r = self.session.get(store_stock_url, params=params, timeout=self.timeout)
        r.raise_for_status()
        
        return r.json()
    
    def _get_store_availability(self, stock_info: dict) -> list[StoreStockLevel]:
        stores = []
        for store in stock_info["stores"]:
            point_of_service = store["pointOfService"]
            
            name = point_of_service["displayName"]
            distance_km = float(point_of_service["formattedDistance"].split(" ")[0].replace(",", "."))
            stock = store["stockInfo"]["stockLevel"]
            
            stores.append(StoreStockLevel(
                name,
                distance_km,
                stock
            ))
            
        return stores
    

    def fetch_wines(self, brand_code: str) -> list[WineProfile]:
        products = self._fetch_all_wines_by_brand(brand_code)
        wines = [self._parse(p, brand_code) for p in products]
        
        for wine in wines:
            if wine.available.in_stores:
                res = self._find_stores_with_wine_in_stock(wine_code=wine.code)
                
                
                wine.available.locally = True # TODO: Fix so locally is only true is store is inside a certain radius
                
                store_availability = self._get_store_availability(res)
                wine.available.stores = store_availability
                wine.available.sort_stores_by_km()
                
        return wines


    def _fetch_all_wines_by_brand(self, brand_code: str) -> list[dict]:
        first_response = self._search(brand_code, page=0)

        products = list(first_response["products"])
        total_pages = first_response["pagination"]["totalPages"]

        for page in range(1, total_pages):
            next_page_response = self._search(brand_code, page=page)
            products.extend(next_page_response["products"])

        return products

    def _search(self, brand_code: str, page: int, page_size: int = 50) -> dict:
        search_url = self.BASE_URL + "/vmpws/v2/vmp/products/search"
        params = {
            "fields": "FULL",
            "pageSize": page_size,
            "currentPage": page,
            "q": f":name-asc:brand:{brand_code}",
        }
        r = self.session.get(search_url, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
    

    def _parse(self, product: dict, brand_code: str) -> WineProfile:
        product_availability = product["productAvailability"]
        online_availability: bool = product_availability["deliveryAvailability"]["availableForPurchase"]
        store_availability: bool = product_availability["storesAvailability"]["availableForPurchase"]
        
        return WineProfile(
            code=product["code"],
            name=product["name"],
            brand_code=brand_code,
            available=Availability(
                online=online_availability,
                in_stores=store_availability
            ),
            price=product["price"]["value"],
            url=f"{self.BASE_URL}{product['url']}",
        )
