from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.description_recommendation import (
    recommend_expense_description,
)

router = APIRouter()


class DescriptionRequest(BaseModel):
    expense: Any

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "expense": {
                        "merchant": "Carrefour",
                        "items": [
                            {"name": "Milk"},
                            {"name": "Bread"},
                        ],
                    }
                }
            ]
        }
    }


@router.post(
    "/recommend-expense-description",
    tags=["Recommendations"],
    summary="Generate a short expense description",
    response_description="A concise human-readable expense description",
)
def recommend_description(
    request: DescriptionRequest,
):
    return recommend_expense_description(
        request.expense
    )
