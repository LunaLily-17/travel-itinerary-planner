"""Find a feasible itinerary within the trip window and admission budget."""

from itertools import permutations

from .attractions import CATALOGUE

TRAVEL_MINUTES = {
    frozenset(("riverside", "viewpoint")): 20,
    frozenset(("riverside", "archive")): 25,
    frozenset(("viewpoint", "archive")): 15,
}


def minutes(value: str) -> int:
    hours, mins = map(int, value.split(":"))
    return hours * 60 + mins


def clock(value: int) -> str:
    hours, mins = divmod(value, 60)
    return f"{hours:02d}:{mins:02d}"


def build_schedule(preferences: dict, candidates: list[str]) -> list[dict]:
    # The catalogue is small. Try the largest schedules first in ranked order.
    for size in range(len(candidates), 0, -1):
        for route in permutations(candidates, size):
            if sum(CATALOGUE[stop]["price_gbp"] for stop in route) > preferences["attraction_budget_gbp"]:
                continue
            visits = []
            end = minutes(preferences["start_time"])
            previous = None
            for stop in route:
                attraction = CATALOGUE[stop]
                travel = 0
                if previous is not None:
                    travel = TRAVEL_MINUTES.get(frozenset((previous, stop)))
                    if travel is None:
                        break
                start = max(end + travel, minutes(attraction["opens"]))
                end = start + attraction["duration_minutes"]
                if end > min(minutes(attraction["closes"]), minutes(preferences["end_time"])):
                    break
                visits.append({"attraction_id": stop, "start_time": clock(start), "end_time": clock(end)})
                previous = stop
            else:
                return visits
    return []
