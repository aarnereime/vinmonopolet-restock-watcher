from dataclasses import dataclass


@dataclass(frozen=True)
class Producer:
    name: str
    brand_code: str


@dataclass
class WineProfile:
    code: str
    name: str
    brand_code: str
    available: bool
    price: float | None
    url: str | None