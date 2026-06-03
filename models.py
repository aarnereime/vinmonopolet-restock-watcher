from dataclasses import dataclass


@dataclass(frozen=True)
class Producer:
    name: str
    brand_code: str
    

@dataclass
class Availability:
    online: bool
    in_stores: bool
    locally: bool | None = None


@dataclass
class WineProfile:
    code: str
    name: str
    brand_code: str
    url: str
    available: Availability
    price: float | None = None