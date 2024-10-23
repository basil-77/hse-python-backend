import sqlite3 as sq


SQL_CREATE_ITEM = """
create table Item(
    id integer primary key autoincrement,
    name text not null,
    price real not null,
    deleted bool not null default 1
    )
"""

SQL_CREATE_CART = """
create table Cart(
    id integer primary key autoincrement,
    price_sum real not null
    )
"""

SQL_CREATE_CARTITEMS = """
create table CartItems(
    cart_id integer not null,
    item_id integer not null,
    quantity integer not null,
    available bool not null default 1,
    foreign key (cart_id) references Cart(id) on update cascade,
    foreign key (item_id) references Item(id) on update cascade
    )
"""

SQL_CREATE_VEW_CARTS_DETAIL = """
    create view carts_sum_amount
    as
    select
    CartItems.cart_id,
    sum(CartItems.quantity) as sum_quantity,
    Item.price * CartItems.quantity as sum_amount
    from CartItems
    inner join Item on CartItems.item_id = Item.id
    where Item.deleted=0
    group by CartItems.cart_id
"""

SQL_NEW_ITEM = """
    insert into Item (name, price, deleted)
    values (?, ?, ?)
"""
SQL_SELECT_ITEM = """
    select * from Item where id = ?
"""

SQL_ROW_ID = """
    select last_insert_rowid()
"""

SQL_UPDATE_ITEM = """
    update Item
    set name = ?,
    price = ?,
    deleted = ?
    where id = ?
"""

SQL_PATCH_ITEM = """
    update Item
    set name = ?,
    price = ?
    where id = ?
"""

SQL_DELETE_ITEM = """
    update Item
    set deleted = 1
    where id = ?
"""

SQL_NEW_CART = """
    insert into Cart (price_sum)
    values (0)
"""

SQL_ADD_ITEM_TO_CART = """
    insert into CartItems (cart_id, item_id, quantity)
    values (?, ?, ?)
"""

SQL_GET_CART = """
    select
    Cart.id as cart_id,
    Item.id as item_id,
    Item.name,
    CartItems.quantity,
    not Item.deleted as available,
    carts_sum_amount.sum_amount,
    carts_sum_amount.sum_quantity
    from Cart
    inner join CartItems on Cart.id = CartItems.cart_id
    inner join Item on CartItems.item_id = Item.id
    inner join carts_sum_amount on cart.id = carts_sum_amount.cart_id
"""

class StoreDB:
    def __init__(self, db_file_name) -> None:
        self.con = sq.connect(db_file_name)
        self.con.row_factory = sq.Row
        self.con.execute(SQL_CREATE_CART)
        self.con.execute(SQL_CREATE_ITEM)
        self.con.execute(SQL_CREATE_CARTITEMS)
        self.con.execute(SQL_CREATE_VEW_CARTS_DETAIL)
            
    def _truncate_all(self):
        #self.con.isolation_level = None
        self.con.execute('delete from CartItems')
        self.con.execute('delete from Item')
        self.con.execute('delete from Cart')
        #self.con.execute('vacuum')
        self.con.execute('delete from SQLITE_SEQUENCE where name="Item"')
        self.con.execute('delete from SQLITE_SEQUENCE where name="Cart"')
        #self.con.isolation_level = ''


    
    def new_item(self, name: str, price: float):
        data = ((name, price, 0))
        try:
            result = self.con.execute(SQL_NEW_ITEM, data)
            new_id = self.con.execute(SQL_ROW_ID).fetchone()['last_insert_rowid()']
            result = self.get_item(new_id)
        except:
            return None
        return result
    
    def get_item(self, id: int):
        data = [(id)]
        try:
            row = self.con.execute(SQL_SELECT_ITEM, data).fetchone()
            result = {}
            for key in row.keys():
                result[key] = row[key]
        except:
            return None
        return result
    
    def get_items_by_query(self, min_price: float | None, max_price: float | None, show_deleted: bool, limit: int | None = 10, offset: int | None = 0):
        sql_str = 'select * from Item where 1=1'
        if min_price:
            sql_str += f' and price >= {min_price}'
        if max_price:
            sql_str += f' and price <={max_price}'
        if not show_deleted:
            sql_str += ' and deleted = 0'
        if limit:
            sql_str += f' limit {limit}'
        if offset:
            sql_str += f' offset {offset}'
        try:
            rows = self.con.execute(sql_str).fetchall()
            result = []
            for row in rows:
                row_dict = {}
                for key in row.keys():
                    row_dict[key] = row[key]
                result.append(row_dict)
        except:
            return None
        return result

    def update_item(self, id: int, name: str, price: float, deleted: bool):
        data = ((name, price, deleted, id))
        try:
            self.con.execute(SQL_UPDATE_ITEM, data)
            result = self.get_item(id)
        except:
            return None
        return result
    
    def patch_item(self, id: int, name: str, price: float):
        data = ((name, price, id))
        try:
            self.con.execute(SQL_PATCH_ITEM, data)
            result = self.get_item(id)
        except:
            return None
        return result
    
    def delete_item(self, id: int):
        data = [(id)]
        try:
            self.con.execute(SQL_DELETE_ITEM, data)
        except:
            return False
        return True
    
    def new_cart(self):
        try:
            self.con.execute(SQL_NEW_CART)
            new_id = self.con.execute(SQL_ROW_ID).fetchone()['last_insert_rowid()']
        except:
            return None
        return new_id

    def add_item_to_cart(self, cart_id: int, item_id: int, quantity: int):
        data = ((cart_id, item_id, quantity))
        try:
            self.con.execute(SQL_ADD_ITEM_TO_CART, data)
        except:
            return False
        return True
    
    def get_cart(self, id: int):
        sql_str = SQL_GET_CART + f' where Cart.id = {id}'
        try:
            rows = self.con.execute(sql_str).fetchall()
            if len(rows) <= 0:
                return None
            result = {'id': id}
            items = []
            cart_sum = 0
            for row in rows:
                row_dict = {}
                for key in row.keys():
                    if key in ['item_id', 'name', 'quantity', 'available']:
                        _key = 'id' if key == 'item_id' else key
                        row_dict[_key] = row[key]
                        cart_sum = row['sum_amount']
                items.append(row_dict)
            result['items'] = items
            result['price'] = cart_sum
        except:
            return None
        return result
        

    def get_cart_by_query(self, min_price: float | None, max_price: float | None, min_quantity: int | None, max_quantity: int | None, limit: int | None = 10, offset: int | None = 0):
        sql_str = f'select * from carts_sum_amount where 1=1'
        if min_price:
            sql_str += f' and sum_amount >= {min_price}'
        if max_price:
            sql_str += f' and sum_amount <= {max_price}'
        if min_quantity:
            sql_str += f' and sum_quantity >= {min_quantity}'
        if max_quantity:
            sql_str += f' and sum_quantity <= {max_quantity}'
        if limit:
            sql_str += f' limit {limit}'
        if offset:
            sql_str += f' offset {offset}'
        try:
            rows = self.con.execute(sql_str).fetchall()
            if rows is None:
                return None
            carts = []
            for row in rows:
                row_dict = {}
                for key in row.keys():
                    row_dict[key] = row[key]
                carts.append(row_dict)
        except:
            return None

        result = []
        for cart in carts:
            result.append(self.get_cart(cart['cart_id']))
        return result

#*******************************************************************************






