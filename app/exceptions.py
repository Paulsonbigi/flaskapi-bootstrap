from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str | None = None):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.detail,
                    "code": exc.error_code,
                    "status": exc.status_code,
                }
            },
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(
        request: Request, exc: ValidationError
    ):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "message": "Validation failed",
                    "code": "VALIDATION_ERROR",
                    "details": exc.errors(),
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "Internal server error",
                    "code": "INTERNAL_ERROR",
                }
            },
        )

# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.config import get_settings
# from app.database import SessionLocal
# from app.exceptions import register_exception_handlers
# from app.middleware import RequestLoggingMiddleware


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Manage application lifecycle: startup and shutdown."""
#     settings = get_settings()

#     # Startup
#     await SessionLocal.init(settings.database_url)
#     yield

#     # Shutdown
#     await SessionLocal.close()


# def create_app() -> FastAPI:
#     settings = get_settings()

#     app = FastAPI(
#         title=settings.app_name,
#         version=settings.app_version,
#         docs_url="/docs" if settings.debug else None,
#         redoc_url="/redoc" if settings.debug else None,
#         lifespan=lifespan,
#     )

#     # Middleware (order matters — last added = first executed)
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=settings.allowed_origins,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )
#     # app.add_middleware(RequestLoggingMiddleware)

#     # Register routes
#     app.include_router(api_router, prefix="/api")

#     # Register exception handlers
#     register_exception_handlers(app)

#     return app


# app = create_app()