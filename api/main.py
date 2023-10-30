""" Main module for REST API """
from typing import Union
from fastapi import FastAPI
from prisma import Prisma
import os 

app = FastAPI()
prisma = Prisma()


@app.get("/")
async def read_root():
    """Function printing python version."""
    for file in os.walk("/workspaces/Picnik"):
        print(file)
    data = {
        'name': 'Robert xx',
        'email': 'robert_xx@craigie.dev'
    }
    return data


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    """Function printing python version."""
    return {"item_id": item_id, "q": q}