from fastapi import FastAPI

from app.routers import description_recommendation, receipt, recommendation


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

@app.get("/")
def home():

    return {
        "status": "running",
        "swagger": "/docs",
        "redoc": "/redoc",
    }
