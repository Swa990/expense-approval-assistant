
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("VLM_API_ENDPOINT"),
    api_key=os.getenv("VLM_API_TOKEN")
)

MODEL_NAME = os.getenv("VLM_MODEL_NAME", "Qwen/Qwen3.5-4B")


REASONING_PROMPT = """
You are an AI expense decision assistant.

Your task is to explain the results of a deterministic expense
policy evaluation and provide a final recommendation.

You will receive:
1. Employee-submitted information.
2. Facts extracted from supporting documents.
3. Retrieved company policy context.
4. Results produced by a Python policy rule engine.

Instructions:

- Treat the Python rule-engine results as authoritative for
  deterministic policy checks.
- Do not recalculate numerical limits.
- Do not invent policy rules or missing facts.
- Explain the identified violations, unmet requirements
  and unknown conditions.
- Distinguish a confirmed policy violation from missing
  information or a condition requiring review.
- APPROVE only when all applicable requirements are satisfied.
- REJECT only when the policy clearly establishes ineligibility.
- Otherwise return REQUIRES_REVIEW.
- Do not claim an expense exceeds a limit unless the rule
  engine explicitly identifies that result.
- Keep the explanation concise.

Return only valid JSON with exactly these fields:

{
    "decision": "APPROVE | REJECT | REQUIRES_REVIEW",
    "decision_reason": "Explanation of the final recommendation.",
    "missing_information": [],
    "policy_rules_used": []
}
"""


def generate_expense_decision(employee_facts, document_facts, policy_context, rule_results):

    reasoning_input = {
        "employee_information": employee_facts,
        "extracted_document_facts": document_facts,
        "company_policy_context": policy_context,
        "deterministic_rule_results": rule_results
    }

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": REASONING_PROMPT
            },
            {
                "role": "user",
                "content": json.dumps(reasoning_input, default=str)
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
        max_tokens=1200
    )

    result = json.loads(response.choices[0].message.content)

    required_fields = [
        "decision",
        "decision_reason",
        "missing_information",
        "policy_rules_used"
    ]

    if not all(field in result for field in required_fields):
        raise ValueError("Invalid LLM decision response.")

    if result["decision"] not in {
        "APPROVE", "REJECT", "REQUIRES_REVIEW"
    }:
        raise ValueError("Invalid decision value.")

    if not isinstance(result["missing_information"], list):
        raise ValueError("missing_information must be a list.")

    if not isinstance(result["policy_rules_used"], list):
        raise ValueError("policy_rules_used must be a list.")

    return result
