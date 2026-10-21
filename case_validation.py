"""Pure, testable validation and routing logic for synthetic cases."""
import json

PRIORITIES = {"low", "medium", "high"}
REQUIRED_AI_FIELDS = {
    "case_id": str,
    "category": str,
    "priority": str,
    "summary": str,
    "missing_information": list,
    "recommended_route": str,
    "confidence": (int, float),
    "rationale": str,
}


class ValidationError(ValueError):
    """Invalid case or AI response; do not automatically route."""


def priority_for_case(case):
    if not isinstance(case, dict):
        raise ValidationError("Case must be an object")
    for key in ("case_id", "case_type"):
        if not isinstance(case.get(key), str) or not case[key].strip():
            raise ValidationError(f"Missing or invalid {key}")
    amount = case.get("amount")
    days = case.get("days_open")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not 0 <= amount < float("inf"):
        raise ValidationError("amount must be a finite non-negative number")
    if isinstance(days, bool) or not isinstance(days, int) or days < 0:
        raise ValidationError("days_open must be a non-negative integer")
    if amount >= 200 or days >= 5:
        return "high"
    if amount >= 100 or days >= 3:
        return "medium"
    return "low"


def parse_ai_response(raw, case):
    if not isinstance(raw, str):
        raise ValidationError("AI response must be text")
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) < 3 or lines[-1].strip() != "```":
            raise ValidationError("Incomplete JSON code fence")
        text = "\n".join(lines[1:-1]).strip()
    try:
        response = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError("AI response is not valid JSON") from exc
    if not isinstance(response, dict):
        raise ValidationError("AI response must be a JSON object")
    for key, expected_type in REQUIRED_AI_FIELDS.items():
        value = response.get(key)
        if not isinstance(value, expected_type) or (expected_type is (int, float) and isinstance(value, bool)):
            raise ValidationError(f"Missing or invalid AI field: {key}")
    if response["case_id"] != case["case_id"]:
        raise ValidationError("AI response case ID does not match input")
    if response["category"] != case["case_type"]:
        raise ValidationError("AI response category does not match input")
    if response["priority"] not in PRIORITIES:
        raise ValidationError("Unknown AI priority")
    if not 0 <= response["confidence"] <= 1:
        raise ValidationError("Confidence must be between 0 and 1")
    if any(not isinstance(item, str) for item in response["missing_information"]):
        raise ValidationError("missing_information must contain strings")
    return response


def review_decision(case, ai_response):
    """Never automatically approve mismatches or malformed responses."""
    expected = priority_for_case(case)
    try:
        result = parse_ai_response(ai_response, case)
    except ValidationError as exc:
        return {"status": "human_review", "reason": str(exc), "rule_priority": expected}
    if result["priority"] != expected:
        return {"status": "human_review", "reason": "Priority disagreement", "rule_priority": expected, "ai_priority": result["priority"]}
    return {"status": "urgent_review" if expected == "high" else "normal_review", "rule_priority": expected, "ai_priority": result["priority"]}
