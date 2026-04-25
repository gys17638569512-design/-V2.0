from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiException(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "msg": message,
            "data": None,
        },
    )


async def _handle_api_exception(_request: Request, exc: ApiException) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


async def _handle_http_exception(_request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "服务器错误"
    return error_response(exc.status_code, message)


async def _handle_validation_exception(
    _request: Request,
    _exc: RequestValidationError,
) -> JSONResponse:
    return error_response(400, "参数错误")


async def _handle_unexpected_exception(
    _request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    try:
        return await call_next(_request)
    except Exception:
        return error_response(500, "服务器错误")


def register_exception_handlers(app: FastAPI) -> None:
    app.middleware("http")(_handle_unexpected_exception)
    app.add_exception_handler(ApiException, _handle_api_exception)
    app.add_exception_handler(HTTPException, _handle_http_exception)
    app.add_exception_handler(RequestValidationError, _handle_validation_exception)
