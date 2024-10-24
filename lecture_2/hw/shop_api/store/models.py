from dataclasses import dataclass

@dataclass(slots=True)
class Item:
    id: int
    name: str
    price: float
    deleted: bool


@dataclass(slots=True)
class CartItems:
    id: int
    name: str
    quantity: int
    available: bool

@dataclass(slots=True)
class Cart:
    id: int
    items: list[CartItems]
    price: float

@dataclass(slots=True)
class ItemInfo:
    id: int
    name: str
    price: float
    deleted: bool

@dataclass(slots=True)
class CartInfo:
    id: int
    items: list[CartItems]
    price: float