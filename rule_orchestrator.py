
from ingestion.input_ingestion import ingest_document
from extraction.fact_extractor import extract_document_facts
from rag.policy_retriever import retrieve_policy
from decision.policy_rule_engine import evaluate_expense_rules
from decision.llm_reasoner import generate_expense_decision


def build_policy_query(employee_facts, document_facts):
    document_types = []

    for document in document_facts:
        for page in document.get("extracted_pages", []):
            document_type = page.get("facts", {}).get("document_type")
            if document_type:
                document_types.append(document_type)

    return (
        f"Expense category: {employee_facts.get('category')}. "
        f"Claim amount: {employee_facts.get('amount')} "
        f"{employee_facts.get('currency', 'INR')}. "
        f"Supporting documents: {', '.join(set(document_types))}. "
        "Retrieve applicable expense limits, eligibility conditions, "
        "approval requirements, supporting document requirements "
        "and exception handling rules."
    )


def process_expense(employee_facts, uploaded_files):
    extracted_documents = []

    # 1. Document ingestion and fact extraction
    for filename, file_bytes in uploaded_files:
        document = ingest_document(filename, file_bytes)
        extracted_facts = extract_document_facts(document)
        extracted_documents.append(extracted_facts)

    # 2. Retrieve relevant company policies
    policy_query = build_policy_query(employee_facts, extracted_documents)
    company_policies = retrieve_policy(policy_query, k=5)

    # 3. Deterministic policy evaluation using Python
    deterministic_results = evaluate_expense_rules(
        employee_facts=employee_facts,
        document_facts=extracted_documents,
        company_policies=company_policies
    )

    # 4. VLM reasoning and final decision
    decision_result = generate_expense_decision(
        employee_facts=employee_facts,
        document_facts=extracted_documents,
        policy_context=deterministic_results["retrieved_policy_context"],
        rule_results=deterministic_results
    )

    # 5. Return final result
    return {
        "decision": decision_result["decision"],
        "decision_reason": decision_result["decision_reason"],
        "missing_information": decision_result["missing_information"],
        "policy_rules_used": decision_result["policy_rules_used"],
        "rule_status": deterministic_results["rule_status"]
    }
