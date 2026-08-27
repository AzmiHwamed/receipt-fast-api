import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

MODEL = os.getenv("OPENAI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = """
You are a careful travel guide.

Write an accurate, engaging description of the exact place supplied by the user.

Rules:
- Use the place name and coordinates together to identify the correct location and avoid similarly named places.
- Write 80 to 120 words in the requested language.
- Mention what the place is known for and what a visitor can expect.
- Return plain text only, without headings, markdown, or citations.
- Do not invent opening hours, prices, ratings, accessibility details, or other precise claims.
- If the identity is uncertain, only use information supported by the supplied place data.
"""


def generate_place_description(
    *,
    name: str,
    latitude: float,
    longitude: float,
    address: str | None,
    place_type: str | None,
    language_code: str,
) -> str:
    place_data = "\n".join(
        [
            f"Place name: {name}",
            f"Coordinates: latitude {latitude}, longitude {longitude}",
            f"Address: {address or 'Not provided'}",
            f"Place type: {place_type or 'Not provided'}",
            f"Output language: {language_code}",
        ]
    )

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": place_data},
        ],
    )
    description = response.choices[0].message.content
    if not description or not description.strip():
        raise RuntimeError("Gemini returned an empty place description")
    return description.strip()
