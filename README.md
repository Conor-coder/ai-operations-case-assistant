# AI Operations Case Assistant

[![Python tests](https://github.com/Conor-coder/ai-operations-case-assistant/actions/workflows/tests.yml/badge.svg)](https://github.com/Conor-coder/ai-operations-case-assistant/actions/workflows/tests.yml)

**A Python + Claude API portfolio prototype demonstrating safe AI-assisted operations workflows, deterministic validation and automated failure testing.**

> **Demo only:** All cases are fictional. No real payments, customer records or operational systems are accessed or modified.

## Why this project exists

An LLM can help summarise and categorise operational cases, but its output should not be trusted blindly. This project combines **illustrative, deterministic Python rules** with a Claude-generated assessment and routes uncertain or failed results to a human reviewer.

## What it demonstrates

- **LLM integration:** builds a prompt and calls the Anthropic Claude Messages API.
- **Structured JSON validation:** checks required fields, types, case identity, priority and confidence range.
- **Independent rules:** calculates priority from amount and days open without relying on the model.
- **Human-in-the-loop safeguards:** disagreement, malformed output and API errors trigger `human_review`.
- **Failure handling:** the app catches API exceptions and does not include raw exception messages in its decision output.
- **Automated tests:** 19 offline `unittest` cases, including `unittest.mock` simulations of valid responses, malformed JSON, priority disagreement and a Claude outage.
- **Continuous integration:** GitHub Actions runs the offline test suite on pushes and pull requests.

## How it works

```text
                    Fictional case
                         |
                +--------+---------+
                |                  |
          Python rules        Claude API
          (rule priority)     (JSON assessment)
                |                  |
                |            Parse + validate
                |                  |
                +--------+---------+
                         |
                Compare priorities
                         |
              +----------+-----------+
              |                      |
       Valid + agreement      Invalid / disagreement
              |                / API unavailable
       Urgent or normal                |
        human review              Human review
```

**Important:** Even when the rules and AI agree, the program returns `urgent_review` or `normal_review`—it does **not** automatically approve or resolve a case.

## Run the tests (no API key needed)

Requires Python 3.11 or a compatible Python 3 version.

```bash
python -m unittest discover -s tests -v
```

The tests run locally without network access or Claude API charges. See [the test suite](tests/) and [GitHub Actions workflow](.github/workflows/tests.yml).

### Simulating Claude being unavailable

```python
from unittest.mock import Mock
from main import process_case

fake_claude = Mock(side_effect=ConnectionError("simulated outage"))
decision = process_case({
    "case_id": "CASE-001",
    "case_type": "payment_dispute",
    "amount": 249.99,
    "days_open": 3,
}, fake_claude)

assert decision["status"] == "human_review"
```

This demonstrates graceful failure without a real external request.

## Run the optional live Claude demo

1. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set your own `ANTHROPIC_API_KEY`. **Never commit the key.**
3. Run:

   ```bash
   python main.py
   ```

The live demo requires an Anthropic API key and may incur API charges. Its model name is configured in `main.py`; you may need to update it to one available to your account.

## Example outcome

The fictional `CASE-001` is a £249.99 payment dispute open for three days. The deterministic rules classify it as `high`. If the AI returns a valid, matching priority, the decision resembles:

```json
{
  "status": "urgent_review",
  "rule_priority": "high",
  "ai_priority": "high"
}
```

If Claude is unavailable, the program instead returns a `human_review` decision, retaining the rule priority and a sanitised error type.

## Repository guide

| File | Purpose |
| --- | --- |
| [`main.py`](main.py) | Prompt, Claude integration and error-safe orchestration |
| [`case_validation.py`](case_validation.py) | Deterministic priority rules and AI response validation |
| [`tests/test_case_validation.py`](tests/test_case_validation.py) | Boundary, JSON and routing tests |
| [`tests/test_mock_api.py`](tests/test_mock_api.py) | Offline mock API and outage tests |
| [`.github/workflows/tests.yml`](.github/workflows/tests.yml) | Automated CI checks |

## Limitations and next steps

This is a **portfolio learning prototype**, not a production fraud, payments, risk or compliance tool. The thresholds are illustrative, the model's confidence is not calibrated, and no formal accuracy evaluation has been conducted. It does not implement authentication, persistent storage, real case ingestion, retry/backoff policies or a user interface.

Possible next improvements: multi-case evaluation datasets, stronger JSON schema constraints, controlled retry/backoff, observability and an analyst review interface.

---

Built to practise practical AI automation engineering: **LLM APIs, Python, validation, testing and human oversight**.
