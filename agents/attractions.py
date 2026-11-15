"""Rank attractions in the fictional demonstration catalogue."""

CATALOGUE = {
    "riverside": {"name": "Riverside Museum", "city": "London", "interests": ("museums", "photography"),
                  "opens": "10:00", "closes": "15:00", "price_gbp": 12, "duration_minutes": 90},
    "viewpoint": {"name": "Market Viewpoint", "city": "London", "interests": ("photography",),
                  "opens": "09:00", "closes": "16:00", "price_gbp": 8, "duration_minutes": 45},
    "archive": {"name": "City Archive Gallery", "city": "London", "interests": ("museums",),
                "opens": "11:00", "closes": "16:00", "price_gbp": 15, "duration_minutes": 60},
}


def select_attractions(preferences: dict) -> list[str]:
    interests = set(preferences["interests"])
    matches = {}
    for attraction_id, attraction in CATALOGUE.items():
        if attraction["city"].casefold() != preferences["city"].casefold():
            continue
        score = len(interests.intersection(attraction["interests"]))
        if (score or not interests) and attraction["price_gbp"] <= preferences["attraction_budget_gbp"]:
            matches[attraction_id] = score
    return sorted(matches, key=lambda attraction_id: (-matches[attraction_id], attraction_id))
