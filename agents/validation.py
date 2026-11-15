"""Check the draft against the original trip constraints and reference data."""

from .attractions import CATALOGUE
from .scheduling import TRAVEL_MINUTES, minutes


def validate_itinerary(preferences: dict, visits: list[dict], candidates: list[str]) -> list[str]:
    if not visits:
        return ["The itinerary has no visits."]

    issues = []
    total = 0
    shortlisted = set(candidates)
    seen = set()
    previous = None
    previous_end = minutes(preferences["start_time"])
    for visit in visits:
        stop = visit["attraction_id"]
        attraction = CATALOGUE.get(stop)
        if attraction is None or attraction["city"].casefold() != preferences["city"].casefold():
            issues.append(f"Unknown attraction for this city: {stop}.")
            continue
        if stop not in shortlisted:
            issues.append(f"{stop} was not shortlisted.")
        try:
            start = minutes(visit["start_time"])
            end = minutes(visit["end_time"])
        except (KeyError, TypeError, AttributeError, ValueError):
            issues.append(f"{stop} has invalid visit times.")
            continue
        if stop in seen:
            issues.append(f"Duplicate visit: {stop}.")
        seen.add(stop)
        travel = 0
        if previous is not None:
            estimate = TRAVEL_MINUTES.get(frozenset((previous, stop)))
            if estimate is None and previous != stop:
                issues.append(f"Missing travel-time estimate from {previous} to {stop}.")
            elif estimate is not None:
                travel = estimate
        if start < max(previous_end + travel, minutes(preferences["start_time"]), minutes(attraction["opens"])):
            issues.append(f"{stop} starts too early or has insufficient travel time.")
        if end > min(minutes(preferences["end_time"]), minutes(attraction["closes"])):
            issues.append(f"{stop} ends after closing or outside the trip window.")
        if end - start != attraction["duration_minutes"]:
            issues.append(f"{stop} has an incorrect visit duration.")
        total += attraction["price_gbp"]
        previous, previous_end = stop, end
    if total > preferences["attraction_budget_gbp"]:
        issues.append("The total admission cost exceeds the budget.")
    return issues
