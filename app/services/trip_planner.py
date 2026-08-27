import json

from app.services.gemini import MODEL, client


SYSTEM_PROMPT = """
You are a practical travel planner and budget coach. Return only valid JSON.
Use the supplied destination, dates, traveler preferences, budget and spending.
Recommend real, well-known monuments and attractions without inventing booking
details or exact prices. Build a realistic day-by-day itinerary and concise,
actionable budget guidance.

Every destination-based itinerary activity must recommend a specific real
venue. Never return a generic activity such as "enjoy the beach", "have lunch",
"shopping", or "free time" without naming a suitable beach, restaurant, market,
park, museum, or other precise place. For meals, name a real restaurant that
matches the requested cuisine. For beach or leisure time, name a real beach,
park, promenade, or venue. Put the venue's official searchable name in
monumentName and its full local address or precise area in location. Transport
items must name the relevant station, stop, airport, or terminal when known.
For every meal item, monumentName is mandatory and must be the official name of
a real restaurant, not a description such as "local restaurant". For seafood
lunch specifically, select and name one real seafood restaurant in or near the
day's route. If you cannot identify a real venue, replace the activity with one
for which you can. placeSearchQuery must contain an unambiguous searchable
venue query including its official name and city; placeType must describe the
venue using one of restaurant, beach, museum, landmark, park, market, station,
airport, hotel, shop, or other.

Return this shape:
{
  "summary": "",
  "budgetGuidance": {
    "status": "under_budget|on_track|at_risk|over_budget",
    "headline": "", "dailyTarget": 0, "projectedTotal": 0, "tips": [""]
  },
  "categoryLimits": [{"categoryName": "", "amount": 0, "reason": ""}],
  "monuments": [{
    "name": "", "description": "", "category": "",
    "estimatedCost": 0, "recommendedDurationMinutes": 0,
    "addressHint": "", "bestTime": "", "latitude": 0, "longitude": 0
  }],
  "itinerary": [{
    "day": 1, "date": "YYYY-MM-DD", "title": "",
    "items": [{
      "time": "09:00", "title": "", "description": "",
      "location": "", "estimatedCost": 0, "monumentName": "",
      "placeSearchQuery": "Official venue name, city",
      "placeType": "restaurant", "latitude": 0, "longitude": 0
    }]
  }]
}
All monetary values must be numbers in the requested trip currency.
For every monument and itinerary item, return the real geographic latitude and
longitude as decimal numbers. Coordinates must point to the named venue or the
closest precise location for the activity, must be within the destination area,
and must never be strings. Use null only when a precise location genuinely
cannot be identified; do not use 0,0 as a placeholder.
Allocate practical limits across only the available expense categories supplied
by the user. The category limit amounts must add up to no more than totalBudget.
Write every user-facing string in the requested languageCode. This includes the
summary, guidance headline and tips, category-limit reasons, monument names and
descriptions, best-time text, itinerary titles, activity descriptions, and
location labels. Keep JSON property names, dates, times, IDs, currency codes,
and numbers unchanged. Preserve official proper names when translating them
would make the place difficult to identify.
"""


def generate_trip_plan(payload: dict) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty model response")
    content = content.replace("```json", "").replace("```", "").strip()
    return json.loads(content)
