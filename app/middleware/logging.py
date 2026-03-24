import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    # Paths to skip logging (health checks, docs — noisy and not useful)
    SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next) -> Response:

        # Skip noisy paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        # Unique ID for tracing this request across log lines
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        # Extract real client IP — handles proxies and load balancers
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or request.headers.get("x-real-ip")
            or (request.client.host if request.client else "unknown")
        )

        # Build path with query string if present
        path = request.url.path
        if request.url.query:
            path = f"{path}?{request.url.query}"

        # Log incoming request
        logger.info(f"[{request_id}] --> {request.method} {path} | IP: {client_ip}")

        # Process the request
        try:
            response = await call_next(request)
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000)
            logger.error(
                f"[{request_id}] <-- {request.method} {path}"
                f" | 500 | {duration_ms}ms | ERROR: {e}"
            )
            raise

        # Log outgoing response
        duration_ms = round((time.time() - start_time) * 1000)

        # Use WARNING for 4xx/5xx so they stand out in logs
        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO

        logger.log(
            log_level,
            f"[{request_id}] <-- {request.method} {path}"
            f" | {response.status_code}"
            f" | {duration_ms}ms"
            f" | IP: {client_ip}"
        )

        # Attach request ID to response so clients can reference it in bug reports
        response.headers["X-Request-ID"] = request_id
        return response
