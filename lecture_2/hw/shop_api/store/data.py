from .db import StoreDB

DB_FILE_NAME = ':memory:' #'data/store.db'


class ShopAPIDataSource():
    store: StoreDB

    def __init__(self):
        self.store = StoreDB(DB_FILE_NAME)
    
    def _truncate_all(self):
        self.store._truncate_all()
    
    def new_item(self, name: str, price: float):
        return self.store.new_item(name, price)
    
    def get_item(self, id: int):
        return self.store.get_item(id)
    
    def get_items_by_query(self, min_price: float | None, max_price: float | None, show_deleted: bool, limit: int | None = 10, offset: int | None = 0):
        return self.store.get_items_by_query(min_price, max_price, show_deleted, limit, offset)

    def update_item(self, id: int, name: str, price: float, deleted: bool):
        return self.store.update_item(id, name, price, deleted)
    
    def patch_item(self, id: int, name: str, price: float):
        return self.store.patch_item(id, name, price)
    
    def delete_item(self, id: int):
        return self.store.delete_item(id)
    
    def new_cart(self):
        return self.store.new_cart()
    
    def add_item_to_cart(self, cart_id: int, item_id: int, quantity: int):
        return self.store.add_item_to_cart(cart_id, item_id, quantity)
    
    def get_cart(self, id: int):
        return self.store.get_cart(id)
    
    def get_cart_by_query(self, min_price: float | None, max_price: float | None, min_quantity: int | None, max_quantity: int | None, limit: int | None = 10, offset: int | None = 0):
        return self.store.get_cart_by_query(min_price, max_price, min_quantity, max_quantity, limit, offset)
    

data = ShopAPIDataSource()
data._truncate_all()