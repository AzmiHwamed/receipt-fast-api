import os
import json

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


MODEL = os.getenv(
    "OPENAI_MODEL",
    "gemini-2.5-flash"
)


SYSTEM_PROMPT = """
You are an expense categorization AI.

Your task:
Given:
1. A list of existing expense categories.
2. An extracted expense/document JSON.

Choose the best expense category.

Rules:

- Prefer an existing category if it matches.
- Do not create a new category if an existing one clearly applies.
- Consider:
  - merchant name
  - purchased items
  - descriptions
  - prices
  - context
- Understand multiple languages.
- A restaurant receipt should match food/dining categories.
- A supermarket receipt should match groceries.
- Fuel stations should match transportation.
- Electronics stores should match electronics.
- If no existing category fits, suggest a new category.
- Suggest description for the Expense .

Return ONLY valid JSON.

If an existing category matches:

{
  "matched": true,
  "expenseType": {
      "id": "",
      "name": ""
  },
  "confidence": 0.0,
  "reason": ""
}


If no category matches:

{
  "matched": false,
  "suggestedExpenseType": {
      "name": "",
      "description": ""
  },
  "confidence": 0.0,
  "reason": ""
}

"""

COMBINED_SYSTEM_PROMPT = """
You are an expense categorization assistant.

Given existing expense categories and receipt data:
1. Match the best existing category, or suggest a new one when none fits.
2. Generate a concise human-readable description, maximum 80 characters.

Return ONLY valid JSON in this exact top-level shape:
{
  "categoryRecommendation": {
    "matched": true,
    "expenseType": {"id": "", "name": ""},
    "confidence": 0.0,
    "reason": ""
  },
  "descriptionRecommendation": {
    "description": ""
  }
}

When no category fits, replace expenseType with:
"suggestedExpenseType": {"name": "", "description": ""}

Prefer existing categories. Consider merchant, items, descriptions, and context.
Do not include prices or IDs in the description. Understand multiple languages.
"""


def _parse_json_response(response):
    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty model response")

    content = content.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON returned:\n{content}") from error


def recommend_expense(expense_types: list, expense: dict):
    categories = [
        {
            "id": item.get("id"),
            "name": item.get("name"),
            "description": item.get("description"),
        }
        for item in expense_types
    ]

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": COMBINED_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {"existingCategories": categories, "expense": expense},
                    ensure_ascii=False,
                    indent=2,
                ),
            },
        ],
    )
    result = _parse_json_response(response)
    if not isinstance(result, dict):
        raise ValueError("Model response must be a JSON object")
    result.setdefault("categoryRecommendation", None)
    result.setdefault("descriptionRecommendation", None)
    return result


def recommend_expense_type(
    expense_types: list,
    expense: dict
):

    # Keep only useful fields
    categories = []

    for item in expense_types:

        categories.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description")
            }
        )


    user_prompt = f"""
Existing expense categories:

{json.dumps(
    categories,
    ensure_ascii=False,
    indent=2
)}


Expense data:

{json.dumps(
    expense,
    ensure_ascii=False,
    indent=2
)}


Select the best category.
"""


    response = client.chat.completions.create(

        model=MODEL,

        temperature=0,

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": user_prompt
            }

        ]

    )


    return _parse_json_response(response)
