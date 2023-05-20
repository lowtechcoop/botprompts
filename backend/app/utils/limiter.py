from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse, Response

from app.config import get_config

config = get_config()

limiter = Limiter(key_func=get_remote_address, default_limits=[config.RATE_LIMIT_GLOBAL])


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Build a JSON response that excludes the details of the rate limit
    that was hit. If no limit is hit, the countdown is added to headers.
    """
    response = JSONResponse({"error": "Rate limit exceeded"}, status_code=429)
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response
