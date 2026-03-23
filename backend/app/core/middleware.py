from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

class ContentSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        
        if content_length and int(content_length) > settings.MAX_REQUEST_SIZE:
            logger.warning(f"Request body too large: {content_length} bytes")
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"}
            )
            
        return await call_next(request)

class AuthPrepMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # TODO: Implement actual JWT/Auth validation here
        # request.state.user = fetch_user(token)
        return await call_next(request)
