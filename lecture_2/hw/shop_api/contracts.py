from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from lecture_2.hw.shop_api.store.models import Item, Cart, CartItems, ItemInfo, CartInfo
from lecture_2.hw.shop_api.store.db import StoreDB


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    @staticmethod
    def get_item(item: Item) -> ItemResponse:
        return ItemResponse(
            id = item['id'],
            name = item['name'],
            price = item['price'],
            deleted = item['deleted']
        )


class CartResponse(BaseModel):
    id: int
    items: list[CartItems]
    price: float


class ItemRequest(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    def as_item_info(self) -> ItemInfo:
        return ItemInfo(id=self.id, name=self.name, price=self.price, deleted=self.deleted)
    

class CartRequest(BaseModel):
    id: int
    items: list[CartItems]
    price: float

    def as_item_info(self) -> ItemInfo:
        return CartInfo(id=self.id, items=self.items, price=self.price)
    

class CartItemResponse(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

    @staticmethod
    def get_cartitem(item: Item) -> CartItemResponse:
        return ItemResponse(
            id = item['id'],
            name = item['name'],
            quantity = item['quantity'],
            available = item['available']
        )

class CartResponse(BaseModel):
    id: int
    items: list[CartItems]
    price: float

    @staticmethod
    def get_cart(cart: Cart) -> CartResponse:
        return CartResponse(
            id = cart['id'],
            items = cart['items'],
            price = cart['price'],
        )    