"""Validate and normalise preferences for a single-day trip."""

from datetime import time
from pprint import pprint


def validate_preferences(request: dict) -> dict:
    city = request["city"].strip()
    start = time.fromisoformat(request["start_time"])
    end = time.fromisoformat(request["end_time"])
    budget = request["attraction_budget_gbp"]

    if not city:
        raise ValueError("Enter a city.")
    if end <= start:
        raise ValueError("The end time must be after the start time.")
    if budget < 0:
        raise ValueError("The attraction budget cannot be negative.")

    return {
        "city": city,
        "start_time": start.strftime("%H:%M"),
        "end_time": end.strftime("%H:%M"),
        "attraction_budget_gbp": budget,
        "interests": [interest.strip().lower() for interest in request["interests"]],
    }


if __name__ == "__main__":
    pprint(validate_preferences({
        "city": "London",
        "start_time": "09:00",
        "end_time": "16:00",
        "attraction_budget_gbp": 30,
        "interests": ["Museums", "Photography"],
    }))
