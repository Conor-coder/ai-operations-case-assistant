"""AI-assisted triage demo using fictional data only."""
import json
import os

from case_validation import ValidationError, priority_for_case, review_decision

CASE = {
    "case_id": "CASE-001",
    "customer_name": "Alex Carter",
    "case_type": "payment_dispute",
    "amount": 249.99,
    "currency": "GBP",
    "description": "Customer says they do not recognise a £249.99 card payment.",
    "days_open": 3,
}


def build_prompt(case):
    return f"""You are an AI operations assistant.
Analyse this fictional case:
{json.dumps(case, indent=2)}
Return ONLY a JSON object with these fields:
case_id, category, priority, summary, missing_information,
recommended_route, confidence, rationale.
Priority must be low, medium or high; confidence must be a number from 0 to 1.
Do not include Markdown or text outside the JSON."""


def analyse_with_claude(case, client):
    """Only this function makes a real external API call."""
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": build_prompt(case)}],
    )
    return message.content[0].text


def process_case(case, ai_call):
    """Accept an injectable AI function so tests can simulate responses offline."""
    rule_priority = priority_for_case(case)
    try:
        ai_response = ai_call(case)
    except Exception as exc:
        # Do not expose potentially sensitive exception details in output.
        return {"status": "human_review", "rule_priority": rule_priority,
                "reason": f"AI service unavailable ({type(exc).__name__})"}
    return review_decision(case, ai_response)


def main():
    from dotenv import load_dotenv
    from anthropic import Anthropic

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY in your local .env file to run the live demo.")
        return
    client = Anthropic(api_key=api_key)
    try:
        decision = process_case(CASE, lambda case: analyse_with_claude(case, client))
    except ValidationError as exc:
        decision = {"status": "human_review", "reason": str(exc)}
    print(json.dumps(decision, indent=2))
    print("Demo only: no real case was routed or changed.")


if __name__ == "__main__":
    main()
