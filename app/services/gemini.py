import os
import json
import base64

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
You are a universal document understanding AI.

You analyze images from any country and any language.

The document can be:
- receipt
- restaurant menu
- invoice
- shopping bill
- ticket
- price list

The language is unknown.
Automatically detect:
- document type
- language
- country


Extraction rules:

- Extract ALL visible information.
- Preserve original product names.
- Do NOT translate names.
- Do NOT invent missing information.
- If something is unreadable return null.
- Detect currency automatically.
- Understand local tax systems.
- Understand different date formats.
- Understand different writing systems:
  Japanese, Chinese, Arabic, Korean, Cyrillic, Latin, etc.
-Always returns Currency in ISO 4217 format (e.g. USD, EUR, JPY, etc.)

Receipt examples:
- merchant name
- address
- phone
- date
- time
- subtotal
- tax
- total
- payment method
- purchased items

Menu examples:
- dish name
- description
- category
- price

Invoice examples:
- invoice number
- customer
- seller
- tax
- totals


Return ONLY valid JSON.

JSON schema:

{
 "document_type":"",
 "language":"",
 "country":"",

 "merchant":"",
 "address":"",
 "phone":"",

 "invoice_number":"",

 "date":"",
 "time":"",

 "currency":"",

 "subtotal":"",
 "tax":"",
 "total":"",

 "payment_method":"",

 "items":[
   {
     "name":"",
     "description":"",
     "quantity":"",
     "unit_price":"",
     "total_price":""
   }
 ],

 "raw_text":""
}


- Carefully inspect the entire image.
- Items are usually located between merchant information and totals.
- Look for:
  - product names
  - quantities
  - prices
  - category names
  - Japanese counters like 点, 個, 本, 枚
  - Chinese 商品
  - Korean 품명
  - Arabic item descriptions

- Do not stop after finding totals.
- If the receipt contains only payment information and no products, return [].

"""



def extract_receipt(image_path: str):

    # Read image
    with open(image_path, "rb") as f:
        image_bytes = f.read()


    # Convert to base64
    image_base64 = base64.b64encode(
        image_bytes
    ).decode()



    response = client.chat.completions.create(

        model=MODEL,

        temperature=0,

        messages=[

            {
                "role":"system",
                "content":SYSTEM_PROMPT
            },


            {
                "role":"user",
                "content":[

                    {
                        "type":"text",
                        "text":
                        """
Analyze this document image.
Detect the language and extract structured information.
"""
                    },


                    {
                        "type":"image_url",
                        "image_url":{
                            "url":
                            f"data:image/jpeg;base64,{image_base64}"
                        }
                    }

                ]
            }

        ]

    )


    content = response.choices[0].message.content


    if not content:
        raise Exception(
            "Empty model response"
        )


    # Remove markdown if model adds it
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