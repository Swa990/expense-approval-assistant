
from ingestion.input_ingestion import ingest_document
from extraction.fact_extractor import extract_document_facts
from rag.policy_retriever import retrieve_policy
from validation.fact_validator import validate_expense


def build_policy_query(employee_facts, document_facts):
    categories = [employee_facts.get("category", "")]
    amounts = [str(employee_facts.get("amount", ""))]
    document_types = []

    for document in document_facts:
        for page in document.get("extracted_pages", []):
            facts = page.get("facts", {})
            if facts.get("document_type"):
                document_types.append(facts["document_type"])

    return (
        f"Expense category: {', '.join(categories)}. "
        f"Claim amount: {', '.join(amounts)}. "
        f"Supporting document types: {', '.join(document_types)}. "
        "Retrieve applicable reimbursement limits, approval requirements, "
        "supporting document requirements, and expense eligibility rules."
    )


def process_expense(employee_facts, uploaded_files):
    extracted_documents = []

    for filename, file_bytes in uploaded_files:
        document = ingest_document(filename, file_bytes)
        extracted_facts = extract_document_facts(document)
        extracted_documents.append(extracted_facts)

    policy_query = build_policy_query(employee_facts, extracted_documents)
    company_policies = retrieve_policy(policy_query, k=5)

    validation_result = validate_expense(
        structured_facts=employee_facts,
        unstructured_facts=extracted_documents,
        company_policies=company_policies
    )

    return {
        "decision": validation_result["decision"],
        "decision_reason": validation_result["decision_reason"],
        "missing_information": validation_result["missing_information"]
    }
