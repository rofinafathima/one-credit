from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as main_router
from app.api.history_routes import router as history_router
from app.config import settings
from app.utils.logging import get_logger
import logging

# Suppress the noisy AFC (Automatic Function Calling) warning from google.genai SDK
logging.getLogger("google.genai.models").setLevel(logging.ERROR)

logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-Powered Misinformation & Fact-Checking Agent Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router, prefix="/api")
app.include_router(history_router, prefix="/api")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "INVALID_INPUT",
                "message": str(exc)
            }
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred."
            }
        },
    )

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "description": "AI-Powered Misinformation & Fact-Checking Agent Backend",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.1.0"
    }

