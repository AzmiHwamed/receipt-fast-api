import json
from typing import Any

from fastapi import APIRouter, HTTPException
from openai import OpenAIError
from pydantic import BaseModel, Field

from app.services.trip_planner import generate_trip_plan


router = APIRouter()


class TripPlanRequest(BaseModel):
    languageCode: str = Field(default="en", min_length=2, max_length=20)
    destination: str = Field(min_length=2, max_length=200)
    country: str | None = Field(default=None, max_length=100)
    startDate: str
    endDate: str
    travelers: int = Field(default=1, ge=1, le=50)
    interests: list[str] = Field(default_factory=list, max_length=20)
    notes: str | None = Field(default=None, max_length=2000)
    currencyCode: str = Field(min_length=3, max_length=3)
    totalBudget: float = Field(gt=0)
    spent: float = Field(default=0, ge=0)
    categorySpending: list[dict[str, Any]] = Field(default_factory=list)
    availableCategories: list[dict[str, Any]] = Field(default_factory=list)


@router.post("/trip-plan", tags=["Trip planning"])
def plan_trip(request: TripPlanRequest):
    try:
        return generate_trip_plan(request.model_dump())
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail=f"Invalid AI response: {exc}") from exc
    except OpenAIError as exc:
        raise HTTPException(
            status_code=502,
            detail="The trip-planning model is unavailable. Check the AI service network access and API configuration.",
        ) from exc
