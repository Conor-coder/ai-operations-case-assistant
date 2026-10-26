import json
import unittest

from case_validation import ValidationError, parse_ai_response, priority_for_case, review_decision


CASE = {"case_id": "CASE-001", "case_type": "payment_dispute", "amount": 249.99, "days_open": 3}


def ai_result(**changes):
    result = {
        "case_id": "CASE-001", "category": "payment_dispute",
        "priority": "high", "summary": "Synthetic payment dispute",
        "missing_information": ["Transaction details"],
        "recommended_route": "Analyst review", "confidence": 0.7,
        "rationale": "Illustrative risk threshold",
    }
    result.update(changes)
    return json.dumps(result)


class PriorityTests(unittest.TestCase):
    def test_low(self):
        self.assertEqual(priority_for_case({**CASE, "amount": 99.99, "days_open": 2}), "low")

    def test_amount_boundaries(self):
        self.assertEqual(priority_for_case({**CASE, "amount": 100, "days_open": 0}), "medium")
        self.assertEqual(priority_for_case({**CASE, "amount": 200, "days_open": 0}), "high")

    def test_days_boundaries(self):
        self.assertEqual(priority_for_case({**CASE, "amount": 0, "days_open": 3}), "medium")
        self.assertEqual(priority_for_case({**CASE, "amount": 0, "days_open": 5}), "high")

    def test_invalid_inputs(self):
        for amount in (-1, "200", True, float("nan")):
            with self.subTest(amount=amount), self.assertRaises(ValidationError):
                priority_for_case({**CASE, "amount": amount})
        with self.assertRaises(ValidationError):
            priority_for_case({**CASE, "days_open": -1})


class ResponseTests(unittest.TestCase):
    def test_valid_json(self):
        self.assertEqual(parse_ai_response(ai_result(), CASE)["priority"], "high")

    def test_fenced_json(self):
        self.assertEqual(parse_ai_response("```json\n" + ai_result() + "\n```", CASE)["priority"], "high")

    def test_bad_json(self):
        with self.assertRaises(ValidationError):
            parse_ai_response("{invalid", CASE)

    def test_wrong_case_id(self):
        with self.assertRaises(ValidationError):
            parse_ai_response(ai_result(case_id="CASE-999"), CASE)

    def test_missing_field(self):
        result = json.loads(ai_result())
        del result["priority"]
        with self.assertRaises(ValidationError):
            parse_ai_response(json.dumps(result), CASE)

    def test_invalid_confidence(self):
        with self.assertRaises(ValidationError):
            parse_ai_response(ai_result(confidence=1.2), CASE)

    def test_boolean_confidence_is_rejected(self):
        with self.assertRaises(ValidationError):
            parse_ai_response(ai_result(confidence=True), CASE)

    def test_invalid_priority(self):
        with self.assertRaises(ValidationError):
            parse_ai_response(ai_result(priority="critical"), CASE)

    def test_disagreement_requires_review(self):
        self.assertEqual(review_decision(CASE, ai_result(priority="low"))["status"], "human_review")

    def test_malformed_response_requires_review(self):
        self.assertEqual(review_decision(CASE, "not json")["status"], "human_review")

    def test_high_agreement_still_requires_urgent_review(self):
        self.assertEqual(review_decision(CASE, ai_result())["status"], "urgent_review")


if __name__ == "__main__":
    unittest.main()
