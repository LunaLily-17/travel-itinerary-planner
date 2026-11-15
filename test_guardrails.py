"""Exercise the Coordinator's approval gate without external services."""

import unittest
from unittest.mock import patch

from agents.scheduling import TRAVEL_MINUTES
from coordinator import plan_trip

REQUEST = {
    "city": "London",
    "start_time": "09:00",
    "end_time": "16:00",
    "attraction_budget_gbp": 30,
    "interests": ["museums", "photography"],
}

DRAFT = [
    {"attraction_id": "riverside", "start_time": "10:00", "end_time": "11:30"},
    {"attraction_id": "archive", "start_time": "11:55", "end_time": "12:55"},
]


class GuardrailTests(unittest.TestCase):
    def assert_rejected(self, result, reason):
        self.assertEqual(result["status"], "validation_failed")
        self.assertNotIn("itinerary", result)
        self.assertTrue(any(reason in issue for issue in result["issues"]), result)

    def test_approved_trip(self):
        result = plan_trip(REQUEST)
        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["admission_total_gbp"], 27)
        self.assertEqual(len(result["itinerary"]), 2)

    def test_invalid_trip_window(self):
        result = plan_trip({**REQUEST, "end_time": "08:00"})
        self.assertEqual(result["status"], "invalid_request")

    def test_no_affordable_stops(self):
        result = plan_trip({**REQUEST, "attraction_budget_gbp": 0})
        self.assertEqual(result["status"], "no_feasible_itinerary")

    def test_rejects_stop_outside_shortlist(self):
        with patch("coordinator.build_schedule", return_value=DRAFT):
            result = plan_trip({**REQUEST, "interests": ["photography"]})
        self.assert_rejected(result, "was not shortlisted")

    def test_rejects_missing_travel_estimate(self):
        with patch.dict(TRAVEL_MINUTES, clear=True):
            with patch("coordinator.build_schedule", return_value=DRAFT):
                result = plan_trip(REQUEST)
        self.assert_rejected(result, "Missing travel-time estimate")

    def test_scheduler_skips_routes_with_no_estimates(self):
        with patch.dict(TRAVEL_MINUTES, clear=True):
            result = plan_trip(REQUEST)
        self.assertEqual(result["status"], "approved")
        self.assertEqual(len(result["itinerary"]), 1)

    def test_rejects_insufficient_travel_gap(self):
        draft = [DRAFT[0], {**DRAFT[1], "start_time": "11:30", "end_time": "12:30"}]
        with patch("coordinator.build_schedule", return_value=draft):
            result = plan_trip(REQUEST)
        self.assert_rejected(result, "insufficient travel time")


if __name__ == "__main__":
    unittest.main()
