import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gemini-2.5-flash",
)

SYSTEM_PROMPT = """
You are an expense assistant.

Given receipt or expense data, generate a short expense description.

Rules:

- Maximum 80 characters.
- Human readable.
- Use merchant name when available.
- Be specific.
- Do not include prices.
- Do not include IDs.
- Return ONLY valid JSON.

Example:

{
  "description": "Groceries from Carrefour"
}
"""


def recommend_expense_description(expense: dict):

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(
                    expense,
                    ensure_ascii=False,
                    indent=2,
                ),
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise Exception("Empty model response")

    content = (
        content.replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(content)