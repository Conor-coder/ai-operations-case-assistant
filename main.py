import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

case = {
    "case_id": "CASE-001",
    "customer_name": "Alex Carter",
    "case_type": "payment_dispute",
    "amount": 249.99,
    "currency": "GBP",
    "description": "Customer says they do not recognise a £249.99 card payment.",
    "days_open": 3
}

case_json = json.dumps(case, indent=2)
print(case_json)

def analyse_case(case_data):
    print("Analysing case:", case_data["case_id"])

    if case_data["amount"] >= 200 or case_data["days_open"] >= 5:
        priority = "high"
    elif case_data["amount"] >= 100 or case_data["days_open"] >= 3:
        priority = "medium"
    else:
        priority = "low"

    result = {
        "case_id": case_data["case_id"],
        "category": case_data["case_type"],
        "priority": priority
    }
    return result

analysis = analyse_case(case)
print(analysis)

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=500,
    messages=[
        {
            "role": "user",
            "content": f"""
You are an AI operations assistant.

Analyse the following case:

{case_json}

Return ONLY valid JSON using exactly this structure:

{{
  "case_id": "string",
  "category": "string",
  "priority": "low, medium, or high",
  "summary": "string",
  "missing_information": ["string"],
  "recommended_route": "string",
  "confidence": 0.0,
  "rationale": "string"
}}

Do not include markdown, headings, or any text outside the JSON.
"""
        }
    ]
)

ai_response = message.content[0].text
clean_response = ai_response.strip()

if clean_response.startswith("```json"):
    clean_response = clean_response[7:]

if clean_response.endswith("```"):
    clean_response = clean_response[:-3]

clean_response = clean_response.strip()
ai_analysis = json.loads(clean_response)
print(ai_analysis)

rule_priority = analysis["priority"]
ai_priority = ai_analysis["priority"]

if rule_priority != ai_priority:
    print("REVIEW REQUIRED: AI and rule-based priorities disagree!")
    print("Rule-based priority:", rule_priority)
    print("AI priority:", ai_priority)
    print("Case held for human review.")
elif rule_priority == "high":
    print("VALIDATION PASSED: Both systems agree.")
    print("URGENT: Route case for immediate review")
else:
    print("VALIDATION PASSED: Both systems agree.")
    print("Route case through normal review process")
