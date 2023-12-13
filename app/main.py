""" Main module for REST API """
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.internal.helper.exception import ServiceException
from app.routers import auth_route, media_route

load_dotenv()
app = FastAPI()

# Add individual routers
app.include_router(auth_route.router)
app.include_router(media_route.router)


@app.exception_handler(ServiceException)
async def unicorn_exception_handler(exc: ServiceException):
    return JSONResponse(
        status_code=400,
        content={
            "error": {"service": exc.name, "message": exc.message},
        },
    )
