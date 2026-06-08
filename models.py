from dataclasses import dataclass


@dataclass(frozen=True)
class Producer:
    name: str
    brand_code: str
    
    
@dataclass
class StoreStockLevel:
    name: str
    distance_km: float
    stock: int
    

@dataclass
class Availability:
    online: bool
    in_stores: bool
    locally: bool | None = None
    stores: list[StoreStockLevel] | None = None

    @property
    def is_available(self) -> bool:
        return self.online or self.in_stores

    def sort_stores_by_km(self) -> None:
        if self.stores:
            self.stores.sort(key=lambda store: store.distance_km)


@dataclass
class WineProfile:
    code: str
    name: str
    brand_code: str
    url: str
    available: Availability
    price: float | None = None