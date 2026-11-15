"""Run the four agents in order and return the outcome."""

from pprint import pprint
from uuid import uuid4

from agents.attractions import CATALOGUE, select_attractions
from agents.preferences import validate_preferences
from agents.scheduling import build_schedule
from agents.validation import validate_itinerary


def plan_trip(request: dict) -> dict:
    request_id = str(uuid4())
    try:
        preferences = validate_preferences(request)
    except (KeyError, TypeError, AttributeError, ValueError) as error:
        return {"request_id": request_id, "status": "invalid_request", "issues": [str(error)]}

    candidates = select_attractions(preferences)
    visits = build_schedule(preferences, candidates)
    if not visits:
        return {"request_id": request_id, "status": "no_feasible_itinerary"}

    issues = validate_itinerary(preferences, visits, candidates)
    if issues:
        return {"request_id": request_id, "status": "validation_failed", "issues": issues}

    itinerary = [
        {**visit, "name": CATALOGUE[visit["attraction_id"]]["name"],
         "price_gbp": CATALOGUE[visit["attraction_id"]]["price_gbp"]}
        for visit in visits
    ]
    return {
        "request_id": request_id,
        "status": "approved",
        "admission_total_gbp": sum(visit["price_gbp"] for visit in itinerary),
        "itinerary": itinerary,
    }


if __name__ == "__main__":
    pprint(plan_trip({
        "city": "London",
        "start_time": "09:00",
        "end_time": "16:00",
        "attraction_budget_gbp": 30,
        "interests": ["Museums", "Photography"],
    }))
