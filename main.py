from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
@app.get('/')
async def root():
    return {'message': 'first message'}

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

@app.get('/other')
def other():
    return {'message': 'this is my other message'}

@app.get('/items/{item_id}')
def read_item(item_id: int, q: str | None = None):
    return {'item_id': item_id, 'q': q}


@app.put('/items/{item_id}')
def update_item(item_id, item: Item):
    return {'item_name': item.name, 'item_price': item.price, 'item_id': item_id}

@app.get("/add")
def add_numbers(first_number: int, second_number: int):
    the_sum = first_number + second_number
    return {"sum": the_sum}