
# import json

# from validation.fact_validator import validate_expense
# from rag.policy_retriever import retrieve_policy


# structured_facts = {
#     "employee_name": "Rahul",
#     "employee_id": "EMP101",
#     "amount": 32000,
#     "currency": "INR",
#     "category": "Medical",
#     "manager_approval": False,
#     "description": "Hospital treatment expenses"
# }

# unstructured_facts = [
#     {
#         "filename": "hospital_bill.pdf",
#         "extracted_pages": [
#             {
#                 "page_number": 1,
#                 "facts": {
#                     "document_type": "hospital_bill",
#                     "vendor_name": "Nobel Hospital",
#                     "transaction_date": "2026-11-01",
#                     "total_amount": 38000,
#                     "currency": "INR",
#                     "expense_category": "Medical",
#                     "confidence": "high"
#                 }
#             }
#         ]
#     }
# ]

# policy_query = """
# Medical expense reimbursement limit, required supporting
# documents and approval requirements.
# """

# company_policies = retrieve_policy(policy_query, k=5)

# result = validate_expense(
#     structured_facts=structured_facts,
#     unstructured_facts=unstructured_facts,
#     company_policies=company_policies
# )

# print(json.dumps(result, indent=4, default=str))



from decision.policy_rule_engine import evaluate_expense_rules
import json

employee_facts = {
    "employee_name": "Rahul",
    "employee_id": "EMP101",
    "amount": 32000,
    "currency": "INR",
    "category": "Medical",
    "manager_approval": False
}

document_facts = [
    {
        "filename": "hospital_bill.pdf",
        "extracted_pages": [
            {
                "page_number": 1,
                "facts": {
                    "document_type": "hospital_bill",
                    "total_amount": 38000,
                    "currency": "INR"
                }
            }
        ]
    }
]

company_policies = [
    {
        "policy_content": """
        Medical Expense Policy:
        - Medical expense reimbursement limit is INR 50,000.
        - Manager approval is mandatory for all expense categories.
        - Claims exceeding INR 50,000 require HR and Finance review.
        - Medical expenses require a hospital bill, medical receipt
          or pharmacy invoice.
        """
    }
]

result = evaluate_expense_rules(
    employee_facts=employee_facts,
    document_facts=document_facts,
    company_policies=company_policies
)

print(json.dumps(result, indent=4, default=str))
