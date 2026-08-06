from fastapi import APIRouter, UploadFile, File

import os
import shutil
import uuid

from app.services.gemini import extract_receipt



router=APIRouter()



@router.post(
    "/receipt",
    tags=["Receipt extraction"],
    summary="Extract data from a receipt or expense document",
    description=(
        "Upload a JPG, PNG, or other image supported by Gemini. The response "
        "contains detected document metadata, merchant details, totals, items, "
        "and raw text. The temporary upload is deleted after processing."
    ),
    response_description="Structured document data extracted by Gemini",
)
async def receipt(
    file:UploadFile=File(
        ...,
        description="Receipt, invoice, menu, ticket, or price-list image",
    )
):

    filename=f"temp_{uuid.uuid4()}.jpg"


    try:
        with open(filename,"wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        return extract_receipt(filename)
    finally:
        if os.path.exists(filename):
            os.remove(filename)
