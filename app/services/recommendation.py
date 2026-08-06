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


    content = response.choices[0].message.content


    if not content:
        raise Exception(
            "Empty model response"
        )


    # Remove markdown fences
    content = content.replace(
        "```json",
        ""
    )

    content = content.replace(
        "```",
        ""
    )

    content = content.strip()


    try:

        result = json.loads(content)

    except json.JSONDecodeError:

        raise Exception(
            f"Invalid JSON returned:\n{content}"
        )


    return result