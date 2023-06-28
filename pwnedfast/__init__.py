from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pwnedfast.errors import http_error, validation_error

def create_app() -> FastAPI:
    app = FastAPI()

    from pwnedfast.controllers import auth_router, users_router
    app.include_router(auth_router)
    app.include_router(users_router)

    app.add_exception_handler(HTTPException, http_error)
    app.add_exception_handler(RequestValidationError, validation_error)

    return app
