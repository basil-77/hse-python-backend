from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, NonNegativeInt, PositiveInt, PositiveFloat, NonNegativeFloat, StrictBool

from lecture_2.hw.shop_api.contracts import CartResponse, ItemResponse, ItemRequest, CartRequest
from lecture_2.hw.shop_api.store.data import data
import json

#from store.db import StoreDB, store
#from queries import items_get_many

class BooleanModel(BaseModel):
    bool_value: bool

router_cart = APIRouter(prefix='/cart')
router_item = APIRouter(prefix='/item')


@router_item.get('/{id}',               
                responses = {
                    HTTPStatus.OK: {'descriotion': 'Succesfully reterned requested item'},
                    HTTPStatus.NOT_FOUND: {'description': 'Failed to return requested item by given id'},
                }
)
async def get_item(id: int) -> ItemResponse:
    item = data.get_item(id)
    if not item:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            'Requested resource item/{id} not found'
        )
    #return ItemResponse.get_item(item)
    item = ItemResponse.get_item(item)
    return({'id': item.id, 'name': item.name, 'price': item.price, 'deleted': item.deleted})

@router_item.get('/')
async def get_items_by_query(
    offset: Annotated[NonNegativeInt | None, Query()] = 0,
    limit: Annotated[PositiveInt | None, Query(lt=25)] = 10,
    min_price: Annotated[NonNegativeFloat | None, Query()] = None,
    max_price: Annotated[NonNegativeFloat | None, Query()] = None,
    show_deleted: bool = False
) -> list[ItemResponse]:
    items = data.get_items_by_query(min_price, max_price, show_deleted, limit, offset)
    return [ItemResponse.get_item(item) for item in items]

@router_item.post(
    '/',
    status_code = HTTPStatus.CREATED
)
async def post_item(info: ItemRequest, response: Response) -> ItemResponse:
    item = info.as_item_info()
    new_item = data.new_item(item.name, item.price)
    id = new_item['id']
    response.headers['location'] = f'/item/{id}'
    #return ItemResponse.get_item(new_item)
    item = ItemResponse.get_item(new_item)
    return({'id': item.id, 'name': item.name, 'price': item.price, 'deleted': item.deleted})


@router_item.put('/{id}',
    responses = {
        HTTPStatus.OK: {'description': 'The item have been succesfully updated.'},
        HTTPStatus.NOT_MODIFIED: {'description': 'Failed to modify the item as one was not found.'}
    }
)
async def put_item(id: int, info: ItemRequest) -> ItemResponse:
    item = data.update_item(info.id, info.name, info.price, info.deleted)
    if not item:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            'Requested resource was not found'
        )
    return ItemResponse.get_item(item)


@router_item.patch('/{id}',
    responses = {
        HTTPStatus.OK: {'description': 'The item have been succesfully patched.'},
        HTTPStatus.NOT_MODIFIED: {'description': 'Failed to modify the item as one was not found.'}
    }
)
async def patch_item(id: int, info: ItemRequest) -> ItemResponse:
    item = data.patch_item(info.id, info.name, info.price)
    if not item:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            'Requested resource was not found'
        )
    return ItemResponse.get_item(item)

@router_item.delete('/{id}')
async def delete_item(id: int) -> Response:
    if not data.delete_item(id):
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            'Requested item was not modified.'
        )
    else:
        return HTTPStatus.OK
    

@router_cart.post(
    '/',
    status_code = HTTPStatus.CREATED
)
async def post_cart(response: Response) -> Response:
    new_cart = data.new_cart()
    #cart = data.get_cart(new_cart)
    response.status_code = HTTPStatus.CREATED
    response.headers['location'] = f'/cart/{new_cart}'
    return {'id': str(new_cart)}


@router_cart.get('/{id}',               
                responses = {
                    HTTPStatus.OK: {'descriotion': 'Succesfully reterned requested cart'},
                    HTTPStatus.NOT_FOUND: {'description': 'Failed to return requested cart by given id'},
                }
)
async def get_cart(id: int) -> CartResponse:
    cart = data.get_cart(id)
    if not cart:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f'Requested resource cart/{id} not found'
        )
    return CartResponse.get_cart(cart)


@router_cart.get('/')
async def get_cart_by_query(
    offset: Annotated[NonNegativeInt | None, Query()] = 0,
    limit: Annotated[PositiveInt | None, Query(lt=25)] = 10,
    min_price: Annotated[NonNegativeFloat | None, Query()] = None,
    max_price: Annotated[NonNegativeFloat | None, Query()] = None,
    min_quantity: Annotated[NonNegativeInt | None, Query()] = None,
    max_quantity: Annotated[NonNegativeInt | None, Query()] = None
) -> list[CartResponse]:
    carts = data.get_cart_by_query(min_price, max_price, min_quantity, max_quantity, limit, offset)
    return [CartResponse.get_cart(cart) for cart in carts]

@router_cart.post('/{cart_id}/add/{item_id}') 
async def add_item_to_cart(cart_id: int, item_id: int) ->Response:
    res = data.add_item_to_cart(cart_id, item_id, quantity=1)
    if res:
        return HTTPStatus.OK
    else:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST,
            'Cannot append the item {item_id} to the cart {cart_id}'
        )