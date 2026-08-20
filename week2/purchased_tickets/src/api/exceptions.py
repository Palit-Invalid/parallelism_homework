from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import DomainError, ObjectLockedError, ObjectNotFound

DOMAIN_ERROR_RESPONSES: dict[type[DomainError], tuple[int, str]] = {
    ObjectLockedError: (
        status.HTTP_409_CONFLICT,
        "Object is being already processed",
    ),
    ObjectNotFound: (
        status.HTTP_404_NOT_FOUND,
        "Object not found",
    ),
}


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_exception_handler(
        _: Request,
        exc: DomainError,
    ) -> JSONResponse:
        status_code, message = _get_domain_error_response(exc)

        return JSONResponse(
            status_code=status_code,
            content={"detail": message},
        )


def _get_domain_error_response(exc: DomainError) -> tuple[int, str]:
    for error_type, response in DOMAIN_ERROR_RESPONSES.items():
        if isinstance(exc, error_type):
            return response

    return status.HTTP_400_BAD_REQUEST, "Unknown error"
