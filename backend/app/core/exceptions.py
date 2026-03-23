from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    formatted_errors = []
    for error in errors:
        formatted_errors.append({
            "loc": " -> ".join([str(loc) for loc in error["loc"]]),
            "msg": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(f"Validation error on {request.url}: {formatted_errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": formatted_errors},
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
