# AI Operations Case Assistant

A Python and Claude API portfolio prototype for AI-assisted operations case triage.

## Overview
This prototype analyses a **fictional** payment dispute using two approaches: deterministic Python priority rules and an AI-generated case assessment. It parses the AI response as JSON, compares priorities, and flags disagreements for human review.

**Current functionality**
- Creates a synthetic case and serializes it to JSON.
- Calculates priority using illustrative Python rules.
- Calls the Anthropic Claude API for summary, classification, missing information, recommended route, confidence, and rationale.
- Removes optional Markdown JSON fences and parses the result.
- Compares rule-based and AI priorities before printing a simulated review route.
- Flags disagreements for human review.

No real payment systems are connected, and no actual cases are routed or modified.

## Technology
Python · Anthropic Claude API · JSON · python-dotenv

## Setup
Install Python 3, then:

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and replace the placeholder with your Anthropic API key. **Never commit or share your `.env` file.**

```bash
python main.py
```

On Windows you can use `py main.py`.

## Workflow
```text
Synthetic case
    |----------------------|
Python priority       Claude API analysis
    |                       |
    |                 JSON parsing
    |-----------------------|
                |
        Compare priorities
                |
       /                 \
   Disagree             Agree
      |                   |
 Human review       Print review route
```

## Example
For CASE-001, a fictional £249.99 payment dispute open for 3 days, the rule-based result is `high`. If the AI agrees, the program prints:

```text
VALIDATION PASSED: Both systems agree.
URGENT: Route case for immediate review
```

If the AI and rules disagree, it instead flags the case for human review.

## Limitations
This is a **learning prototype**, not a production fraud, risk, or compliance tool. The rules are illustrative rather than official policy. AI-generated procedural or regulatory claims must be verified. The model's confidence score is not calibrated. JSON parsing may fail on malformed responses; exception handling, schema validation, multi-case tests, and measured evaluations are planned. All data should remain synthetic, and any real-world decision would require appropriate human oversight.

## Next improvements
- JSON schema validation and robust error handling
- Multiple synthetic cases and automated tests
- Measured accuracy and consistency
- API/database integration and analyst interface

Built as a hands-on AI automation portfolio project.
