""" Main module for REST API """
from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv

from api.routers import media_route
from api.routers import auth_route

load_dotenv()
app = FastAPI()

# Add individual routers
app.include_router(auth_route.router)
app.include_router(media_route.router)


@app.get("/items/{item}")
def read_item(item_id: int, q: Union[str, None] = None):
    """Function printing python version."""
    return {"item_id": item_id, "q": q}
