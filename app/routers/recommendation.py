from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.recommendation import (
    recommend_expense,
    recommend_expense_type
)


router = APIRouter()


class ExpenseType(BaseModel):

    id: str

    name: str

    description: str | None = None



class RecommendationRequest(BaseModel):

    expense_types: list[ExpenseType]

    expense: Any

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "expense_types": [
                        {
                            "id": "groceries",
                            "name": "Groceries",
                            "description": "Supermarket and food purchases",
                        },
                        {
                            "id": "dining",
                            "name": "Dining",
                            "description": "Restaurants and cafes",
                        },
                    ],
                    "expense": {
                        "merchant": "Carrefour",
                        "items": [{"name": "Milk"}, {"name": "Bread"}],
                        "currency": "EUR",
                    },
                }
            ]
        }
    }


@router.post(
    "/recommend-expense",
    tags=["Recommendations"],
    summary="Recommend an expense category and description in one AI request",
)
def recommend_combined(request: RecommendationRequest):
    return recommend_expense(
        expense_types=[item.model_dump() for item in request.expense_types],
        expense=request.expense,
    )



@router.post(
    "/recommend-expense-type",
    tags=["Recommendations"],
    summary="Recommend the best expense category",
    response_description="The matched category or a suggested new category",
)
def recommend(request: RecommendationRequest):

    result = recommend_expense_type(
        expense_types=[
            item.model_dump()
            for item in request.expense_types
        ],
        expense=request.expense
    )


    return result
