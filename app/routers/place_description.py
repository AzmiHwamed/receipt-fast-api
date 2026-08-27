from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.place_description import generate_place_description


router = APIRouter()


class PlaceDescriptionRequest(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str | None = Field(default=None, max_length=1000)
    place_type: str | None = Field(default=None, max_length=200)
    language_code: str = Field(default="en", min_length=2, max_length=20)


@router.post(
    "/place-description",
    tags=["Places"],
    summary="Generate a travel description for a place",
)
def describe_place(request: PlaceDescriptionRequest):
    try:
        description = generate_place_description(
            name=request.name,
            latitude=request.latitude,
            longitude=request.longitude,
            address=request.address,
            place_type=request.place_type,
            language_code=request.language_code,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"description": description}
