"""HTTP entry point for the travel itinerary prototype."""

from typing import Annotated

from fastapi import FastAPI, Response
from pydantic import BaseModel, Field

from coordinator import plan_trip

app = FastAPI(title="Travel Itinerary Planner")

ClockTime = Annotated[str, Field(pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")]


class TripRequest(BaseModel):
    city: str
    start_time: ClockTime
    end_time: ClockTime
    attraction_budget_gbp: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    interests: list[str]


@app.post("/itineraries")
def create_itinerary(request: TripRequest, response: Response) -> dict:
    result = plan_trip(request.model_dump())
    if result["status"] == "invalid_request":
        response.status_code = 422
    elif result["status"] == "validation_failed":
        response.status_code = 500
    return result
