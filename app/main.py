from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from app.core.config import settings
from app.api.api import api_router
from app.schemas.response import APIResponse, ErrorDetails
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware

# Setup logging on startup
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", response_model=APIResponse)
async def root():
    return APIResponse(
        success=True,
        message="Welcome to BRO-Website API"
    )

@app.get("/health", response_model=APIResponse)
async def health_check():
    return APIResponse(
        success=True,
        message="Health check passed",
        data={"status": "ok"}
    )

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP {exc.status_code} error: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            success=False,
            message=exc.detail if isinstance(exc.detail, str) else "Request failed",
            meta={"path": request.url.path, "method": request.method},
            error=ErrorDetails(code=f"HTTP_{exc.status_code}", details=exc.detail)
        ).model_dump(mode='json')
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code} error: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            success=False,
            message=exc.detail if isinstance(exc.detail, str) else "Request failed",
            meta={"path": request.url.path, "method": request.method},
            error=ErrorDetails(code=f"HTTP_{exc.status_code}", details=exc.detail)
        ).model_dump(mode='json')
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = {}
    for error in exc.errors():
        field = error["loc"][-1]
        message = error["msg"]
        error_details[field] = message
    
    logger.warning(f"Validation error: {error_details} - Path: {request.url.path}")
    return JSONResponse(
        status_code=422,
        content=APIResponse(
            success=False,
            message="Validation failed",
            meta={"path": request.url.path, "method": request.method},
            error=ErrorDetails(code="VALIDATION_ERROR", details=error_details)
        ).model_dump(mode='json')
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=APIResponse(
            success=False,
            message="Internal Server Error",
            meta={"path": request.url.path, "method": request.method},
            error=ErrorDetails(code="INTERNAL_ERROR", details=str(exc))
        ).model_dump(mode='json')
    )
