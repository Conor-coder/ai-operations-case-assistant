"""Offline tests for the Claude integration boundary: no API key or network needed."""
import json
import unittest
from unittest.mock import Mock

from main import process_case

CASE = {"case_id": "CASE-001", "case_type": "payment_dispute",
        "amount": 249.99, "days_open": 3}

def response(priority="high"):
    return json.dumps({
        "case_id": CASE["case_id"], "category": CASE["case_type"],
        "priority": priority, "summary": "Fictional dispute",
        "missing_information": [], "recommended_route": "Analyst review",
        "confidence": 0.8, "rationale": "Illustrative test",
    })

class MockAPITests(unittest.TestCase):
    def test_valid_response_routes_to_urgent_review(self):
        fake_claude = Mock(return_value=response())
        result = process_case(CASE, fake_claude)
        self.assertEqual(result["status"], "urgent_review")
        fake_claude.assert_called_once_with(CASE)

    def test_malformed_response_routes_to_human_review(self):
        fake_claude = Mock(return_value="not valid JSON")
        result = process_case(CASE, fake_claude)
        self.assertEqual(result["status"], "human_review")
        self.assertEqual(result["rule_priority"], "high")

    def test_priority_disagreement_routes_to_human_review(self):
        fake_claude = Mock(return_value=response(priority="low"))
        result = process_case(CASE, fake_claude)
        self.assertEqual(result["status"], "human_review")
        self.assertEqual(result["reason"], "Priority disagreement")

    def test_claude_unavailable_routes_to_human_review(self):
        fake_claude = Mock(side_effect=ConnectionError("simulated outage"))
        result = process_case(CASE, fake_claude)
        self.assertEqual(result["status"], "human_review")
        self.assertEqual(result["rule_priority"], "high")
        self.assertIn("ConnectionError", result["reason"])
        self.assertNotIn("simulated outage", result["reason"])
        fake_claude.assert_called_once_with(CASE)

if __name__ == "__main__":
    unittest.main()
