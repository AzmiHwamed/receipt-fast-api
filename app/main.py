from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import RateLimitError

from app.routers import (
    description_recommendation,
    place_description,
    receipt,
    recommendation,
    trip_planner,
)


app = FastAPI(
    title="Gemini Receipt OCR API",
    description=(
        "Upload receipts or other expense documents for structured extraction, "
        "then generate expense category and description recommendations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Receipt extraction",
            "description": "Extract structured data from an uploaded document image.",
        },
        {
            "name": "Recommendations",
            "description": "Recommend an expense category or a short description.",
        },
    ],
)


@app.exception_handler(RateLimitError)
async def ai_rate_limit_handler(_request: Request, error: RateLimitError):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "AI provider quota exhausted. Please retry later.",
            "providerStatus": 429,
        },
        headers={"Retry-After": "60"},
    )


app.include_router(
    receipt.router,
    prefix="/ai"
)


app.include_router(
    recommendation.router,
    prefix="/ai"
)

app.include_router(recommendation.router)

app.include_router(
    description_recommendation.router
)

app.include_router(
    place_description.router,
    prefix="/ai",
)

app.include_router(trip_planner.router, prefix="/ai")

@app.get("/")
def home():

    return {
        "status": "running",
        "swagger": "/docs",
        "redoc": "/redoc",
    }
