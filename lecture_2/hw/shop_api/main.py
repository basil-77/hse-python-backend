from fastapi import FastAPI
from lecture_2.hw.shop_api.store.db import StoreDB
from lecture_2.hw.shop_api.routes import router_cart, router_item
from lecture_2.hw.shop_api.store.data import ShopAPIDataSource

app = FastAPI(title='Shop API')
app.include_router(router_cart)
app.include_router(router_item)

data = ShopAPIDataSource()
