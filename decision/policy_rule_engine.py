
# import re
# from decimal import Decimal, InvalidOperation


# def to_decimal(value):
#     try:
#         if value is None:
#             return None
#         return Decimal(str(value).replace(",", "").replace("₹", "").strip())
#     except (InvalidOperation, ValueError, TypeError):
#         return None


# def normalize(value):
#     return str(value or "").strip().lower().replace("_", " ")


# def flatten_document_facts(documents):
#     extracted = []

#     for document in documents or []:
#         filename = document.get("filename", "Unknown")

#         for page in document.get("extracted_pages", []):
#             facts = page.get("facts", {})
#             extracted.append({
#                 **facts,
#                 "source": filename
#             })

#     return extracted


# def extract_policy_text(company_policies):
#     policy_text = []

#     for policy in company_policies or []:
#         content = policy.get("policy_content", "")
#         if content:
#             policy_text.append(content)

#     return "\n".join(policy_text)


# def extract_category_limit(policy_text, category):
#     lines = policy_text.splitlines()
#     category_found = False

#     for line in lines:
#         normalized_line = normalize(line)

#         if category in normalized_line and (
#             "expense" in normalized_line or "limit" in normalized_line
#         ):
#             category_found = True

#         if category_found:
#             match = re.search(
#                 r"(?:limit|maximum|up to|not exceed)[^\d₹]*₹?\s*([\d,]+(?:\.\d+)?)",
#                 line,
#                 re.IGNORECASE
#             )

#             if match:
#                 return to_decimal(match.group(1))

#     return None


# def evaluate_expense_rules(employee_facts, document_facts, company_policies):
#     results = []
#     violations = []
#     unmet_requirements = []
#     missing_information = []
#     unknown_conditions = []

#     policy_text = extract_policy_text(company_policies)
#     documents = flatten_document_facts(document_facts)

#     category = normalize(employee_facts.get("category"))
#     amount = to_decimal(employee_facts.get("amount"))
#     currency = normalize(employee_facts.get("currency", "INR"))

#     # Validate input facts
#     if amount is None:
#         unknown_conditions.append("Claim amount is missing or invalid.")

#     if not category:
#         unknown_conditions.append("Expense category is missing.")

#     if not policy_text:
#         unknown_conditions.append("No applicable company policy was retrieved.")

#     # Evaluate policy limit
#     policy_limit = extract_category_limit(policy_text, category)

#     if policy_limit is None:
#         unknown_conditions.append(
#             f"No readable numerical limit was found for {category or 'the expense category'}."
#         )
#         results.append({
#             "rule": "Expense limit",
#             "status": "UNKNOWN",
#             "reason": "Applicable policy limit could not be established."
#         })
#     elif amount is not None:
#         if currency != "inr":
#             unknown_conditions.append(
#                 "Policy limit comparison requires a supported currency."
#             )
#         elif amount > policy_limit:
#             reason = (
#                 f"Claim amount {amount} exceeds the retrieved policy limit "
#                 f"of {policy_limit}."
#             )
#             unmet_requirements.append(reason)
#             results.append({
#                 "rule": "Expense limit",
#                 "status": "REQUIRES_REVIEW",
#                 "reason": reason
#             })
#         else:
#             results.append({
#                 "rule": "Expense limit",
#                 "status": "COMPLIANT",
#                 "reason": f"Claim amount {amount} is within policy limit {policy_limit}."
#             })

#     # Evaluate manager approval
#     manager_approval = employee_facts.get("manager_approval")

#     if re.search(
#         r"manager approval.{0,60}(?:mandatory|required)|"
#         r"(?:mandatory|required).{0,60}manager approval",
#         policy_text,
#         re.IGNORECASE
#     ):
#         if manager_approval is True:
#             results.append({
#                 "rule": "Manager approval",
#                 "status": "COMPLIANT",
#                 "reason": "Manager approval is provided."
#             })
#         elif manager_approval is False:
#             reason = "Manager approval has been rejected."
#             violations.append(reason)
#             results.append({
#                 "rule": "Manager approval",
#                 "status": "NON_COMPLIANT",
#                 "reason": reason
#             })
#         else:
#             reason = "Manager approval is missing."
#             unmet_requirements.append(reason)
#             missing_information.append("Manager approval")
#             results.append({
#                 "rule": "Manager approval",
#                 "status": "REQUIRES_REVIEW",
#                 "reason": reason
#             })

#     # Compare submitted claim with extracted document amounts
#     document_amounts = []

#     for document in documents:
#         for field in ("total_amount", "invoice_amount", "bill_amount", "amount_due"):
#             document_amount = to_decimal(document.get(field))
#             if document_amount is not None:
#                 document_amounts.append({
#                     "amount": document_amount,
#                     "source": document["source"]
#                 })
#                 break

#     if amount is not None and document_amounts:
#         matching_amount = any(
#             item["amount"] == amount for item in document_amounts
#         )

#         if matching_amount:
#             results.append({
#                 "rule": "Claim and document amount comparison",
#                 "status": "COMPLIANT",
#                 "reason": "Claim amount matches a supporting document."
#             })
#         else:
#             reason = "Claim amount differs from the extracted document amount."
#             violations.append(reason)
#             missing_information.append("Clarification for amount discrepancy")
#             results.append({
#                 "rule": "Claim and document amount comparison",
#                 "status": "NON_COMPLIANT",
#                 "reason": reason,
#                 "document_amounts": [
#                     {
#                         "amount": str(item["amount"]),
#                         "source": item["source"]
#                     }
#                     for item in document_amounts
#                 ]
#             })
#     else:
#         unknown_conditions.append(
#             "Document amount could not be verified."
#         )

#     # Determine overall rule evaluation status
#     if violations:
#         rule_status = "NON_COMPLIANT"
#     elif unmet_requirements or unknown_conditions:
#         rule_status = "REQUIRES_REVIEW"
#     else:
#         rule_status = "COMPLIANT"

#     return {
#         "rule_status": rule_status,
#         "rule_results": results,
#         "policy_violations": violations,
#         "unmet_requirements": unmet_requirements,
#         "missing_information": missing_information,
#         "unknown_conditions": unknown_conditions,
#         "retrieved_policy_context": policy_text
#     }



import re
import hashlib
from decimal import Decimal, InvalidOperation


def to_decimal(value):
    try:
        if value is None:
            return None
        return Decimal(str(value).replace(",", "").replace("₹", "").strip())
    except (InvalidOperation, ValueError, TypeError):
        return None


def normalize(value):
    return str(value or "").strip().lower().replace("_", " ")


def flatten_document_facts(documents):
    extracted = []

    for document in documents or []:
        filename = document.get("filename", "Unknown")
        pages = document.get("extracted_pages", [])

        if not pages:
            extracted.append({
                "source": filename,
                "facts": {},
                "unreadable": True
            })
            continue

        for page in pages:
            extracted.append({
                **page.get("facts", {}),
                "source": filename,
                "page_number": page.get("page_number")
            })

    return extracted


def extract_policy_text(company_policies):
    policy_text = []

    for policy in company_policies or []:
        content = policy.get("policy_content", "")
        if content:
            policy_text.append(content)

    return "\n".join(policy_text)


def extract_category_limit(policy_text, category):
    lines = policy_text.splitlines()
    category_found = False

    for line in lines:
        normalized_line = normalize(line)

        if category in normalized_line and (
            "expense" in normalized_line or "limit" in normalized_line
        ):
            category_found = True

        if category_found:
            match = re.search(
                r"(?:limit|maximum|up to|not exceed)[^\d₹]*₹?\s*([\d,]+(?:\.\d+)?)",
                line,
                re.IGNORECASE
            )

            if match:
                return to_decimal(match.group(1))

    return None


def add_result(results, rule, status, reason, source=None):
    result = {
        "rule": rule,
        "status": status,
        "reason": reason
    }

    if source:
        result["source"] = source

    results.append(result)


def evaluate_expense_rules(employee_facts, document_facts, company_policies):
    results = []
    violations = []
    unmet_requirements = []
    missing_information = []
    unknown_conditions = []
    exceptions = []

    policy_text = extract_policy_text(company_policies)
    documents = flatten_document_facts(document_facts)

    category = normalize(employee_facts.get("category"))
    amount = to_decimal(employee_facts.get("amount"))
    currency = normalize(employee_facts.get("currency", "INR"))

    # 1. Employee input validation
    required_fields = ["employee_name", "amount", "category"]

    for field in required_fields:
        if employee_facts.get(field) in (None, ""):
            reason = f"Employee information '{field}' is missing."
            missing_information.append(field)
            exceptions.append({
                "type": "MISSING_EMPLOYEE_INFORMATION",
                "field": field,
                "reason": reason
            })

    if amount is None or amount <= 0:
        reason = "Claim amount is missing, invalid or non-positive."
        unknown_conditions.append(reason)
        exceptions.append({
            "type": "INVALID_AMOUNT",
            "reason": reason
        })

    if currency != "inr":
        reason = f"Currency '{currency}' is not supported by the current policy evaluator."
        unknown_conditions.append(reason)
        exceptions.append({
            "type": "UNSUPPORTED_CURRENCY",
            "reason": reason
        })

    if not policy_text:
        reason = "No applicable company policy was retrieved."
        unknown_conditions.append(reason)
        exceptions.append({
            "type": "POLICY_NOT_AVAILABLE",
            "reason": reason
        })

    # 2. Expense category validation
    if category and policy_text:
        category_mentioned = bool(
            re.search(rf"\b{re.escape(category)}\b", policy_text, re.IGNORECASE)
        )

        if not category_mentioned:
            reason = f"No applicable policy was found for category '{category}'."
            unknown_conditions.append(reason)
            exceptions.append({
                "type": "UNKNOWN_EXPENSE_CATEGORY",
                "reason": reason
            })

    # 3. Policy limit validation
    policy_limit = extract_category_limit(policy_text, category) if category else None

    if policy_limit is None:
        reason = f"No readable numerical limit was found for '{category or 'expense category'}'."
        unknown_conditions.append(reason)
        add_result(results, "Expense limit", "UNKNOWN", reason)

    elif amount is not None and currency == "inr":
        if amount > policy_limit:
            reason = (
                f"Claim amount {amount} exceeds the retrieved policy limit "
                f"of {policy_limit}."
            )
            unmet_requirements.append(reason)
            exceptions.append({
                "type": "EXPENSE_LIMIT_EXCEEDED",
                "reason": reason
            })
            add_result(results, "Expense limit", "REQUIRES_REVIEW", reason)
        else:
            add_result(
                results,
                "Expense limit",
                "COMPLIANT",
                f"Claim amount {amount} is within policy limit {policy_limit}."
            )

    # 4. Manager approval validation
    manager_approval = employee_facts.get("manager_approval")

    approval_required = bool(
        re.search(
            r"manager approval.{0,60}(?:mandatory|required)|"
            r"(?:mandatory|required).{0,60}manager approval",
            policy_text,
            re.IGNORECASE
        )
    )

    if approval_required:
        if manager_approval is True:
            add_result(
                results,
                "Manager approval",
                "COMPLIANT",
                "Manager approval is provided."
            )

        elif manager_approval is False:
            reason = "Manager approval has been rejected."
            violations.append(reason)
            exceptions.append({
                "type": "MANAGER_APPROVAL_REJECTED",
                "reason": reason
            })
            add_result(results, "Manager approval", "NON_COMPLIANT", reason)

        else:
            reason = "Manager approval is missing."
            unmet_requirements.append(reason)
            missing_information.append("Manager approval")
            exceptions.append({
                "type": "MANAGER_APPROVAL_MISSING",
                "reason": reason
            })
            add_result(results, "Manager approval", "REQUIRES_REVIEW", reason)

    # 5. Supporting document validation
    if not documents:
        reason = "No supporting documents were uploaded."
        missing_information.append("Supporting documents")
        exceptions.append({
            "type": "MISSING_DOCUMENT",
            "reason": reason
        })
        add_result(results, "Supporting documents", "REQUIRES_REVIEW", reason)

    for document in documents:
        source = document.get("source", "Unknown")

        if document.get("unreadable") or not document:
            reason = "Document content could not be extracted."
            unknown_conditions.append(reason)
            exceptions.append({
                "type": "UNREADABLE_DOCUMENT",
                "source": source,
                "reason": reason
            })
            add_result(results, "Document readability", "UNKNOWN", reason, source)
            continue

        if not document.get("document_type"):
            reason = "Document type could not be identified."
            unknown_conditions.append(reason)
            exceptions.append({
                "type": "UNKNOWN_DOCUMENT_TYPE",
                "source": source,
                "reason": reason
            })

        if not document.get("transaction_date"):
            exceptions.append({
                "type": "MISSING_TRANSACTION_DATE",
                "source": source,
                "reason": "Transaction date could not be extracted."
            })

        document_amount = None

        for field in ("total_amount", "invoice_amount", "bill_amount", "amount_due"):
            document_amount = to_decimal(document.get(field))
            if document_amount is not None:
                break

        if document_amount is None:
            reason = "Document amount could not be extracted."
            unknown_conditions.append(reason)
            exceptions.append({
                "type": "MISSING_DOCUMENT_AMOUNT",
                "source": source,
                "reason": reason
            })

    # 6. Compare claim amount with supporting document amounts
    document_amounts = []

    for document in documents:
        for field in ("total_amount", "invoice_amount", "bill_amount", "amount_due"):
            document_amount = to_decimal(document.get(field))

            if document_amount is not None:
                document_amounts.append({
                    "amount": document_amount,
                    "source": document["source"]
                })
                break

    unique_amounts = {item["amount"] for item in document_amounts}

    if len(unique_amounts) > 1:
        reason = "Conflicting amounts were extracted from supporting documents."
        unknown_conditions.append(reason)
        exceptions.append({
            "type": "CONFLICTING_DOCUMENT_AMOUNTS",
            "reason": reason,
            "evidence": [
                {
                    "amount": str(item["amount"]),
                    "source": item["source"]
                }
                for item in document_amounts
            ]
        })
        add_result(results, "Document amount consistency", "UNKNOWN", reason)

    elif amount is not None and document_amounts:
        document_amount = document_amounts[0]["amount"]

        if amount == document_amount:
            add_result(
                results,
                "Claim and document amount comparison",
                "COMPLIANT",
                "Claim amount matches the supporting document."
            )
        else:
            reason = (
                f"Claim amount {amount} differs from document amount "
                f"{document_amount}."
            )

            # Treat as an exception requiring clarification, not proof of fraud.
            unmet_requirements.append(reason)
            missing_information.append("Clarification for amount discrepancy")
            exceptions.append({
                "type": "CLAIM_DOCUMENT_AMOUNT_MISMATCH",
                "reason": reason,
                "document_amounts": [
                    {
                        "amount": str(item["amount"]),
                        "source": item["source"]
                    }
                    for item in document_amounts
                ]
            })

            add_result(
                results,
                "Claim and document amount comparison",
                "REQUIRES_REVIEW",
                reason
            )

    elif not document_amounts:
        unknown_conditions.append("Document amount could not be verified.")

    # 7. Duplicate document detection using filename and extracted facts
    seen_documents = set()

    for document in documents:
        source = document.get("source", "Unknown")
        identity = (
            source.lower(),
            str(document.get("receipt_number", "")).strip().lower()
        )

        if identity in seen_documents:
            reason = f"Repeated document or receipt detected: {source}."
            exceptions.append({
                "type": "POSSIBLE_DUPLICATE_DOCUMENT",
                "source": source,
                "reason": reason
            })
            unknown_conditions.append(reason)
        else:
            seen_documents.add(identity)

    # 8. Duplicate receipt number detection across different files
    receipt_sources = {}

    for document in documents:
        receipt_number = str(document.get("receipt_number", "")).strip().lower()

        if receipt_number:
            receipt_sources.setdefault(receipt_number, []).append(
                document.get("source", "Unknown")
            )

    for receipt_number, sources in receipt_sources.items():
        if len(set(sources)) > 1:
            reason = f"Receipt number '{receipt_number}' appears in multiple documents."
            exceptions.append({
                "type": "POSSIBLE_DUPLICATE_RECEIPT",
                "reason": reason,
                "sources": list(set(sources))
            })
            unknown_conditions.append(reason)

    # 9. Policy ambiguity checks
    ambiguous_terms = [
        "may be approved",
        "subject to approval",
        "case by case",
        "management discretion",
        "as applicable",
        "where necessary"
    ]

    for term in ambiguous_terms:
        if term in policy_text.lower():
            reason = f"Policy contains an ambiguous condition: '{term}'."
            unknown_conditions.append(reason)
            exceptions.append({
                "type": "AMBIGUOUS_POLICY_CONDITION",
                "reason": reason
            })

    # 10. Final deterministic status
    if violations:
        rule_status = "NON_COMPLIANT"
    elif unmet_requirements or unknown_conditions:
        rule_status = "REQUIRES_REVIEW"
    else:
        rule_status = "COMPLIANT"

    return {
        "rule_status": rule_status,
        "rule_results": results,
        "policy_violations": list(dict.fromkeys(violations)),
        "unmet_requirements": list(dict.fromkeys(unmet_requirements)),
        "missing_information": list(dict.fromkeys(missing_information)),
        "unknown_conditions": list(dict.fromkeys(unknown_conditions)),
        "exceptions": exceptions,
        "retrieved_policy_context": policy_text
    }
