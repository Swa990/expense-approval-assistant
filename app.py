
# import streamlit as st
# from decimal import Decimal
# from orchestrator import process_expense

# st.set_page_config(page_title="AI Expense Decision Assistant", page_icon="💼", layout="centered")

# st.title("AI Expense Decision Assistant")
# st.write("Submit employee expense details and supporting documents for automated validation.")

# with st.form("expense_form"):
#     st.subheader("Employee Information")

#     employee_name = st.text_input("Employee Name")
#     employee_id = st.text_input("Employee ID")

#     st.subheader("Expense Details")

#     amount = st.number_input("Claim Amount (INR)", min_value=0.01, step=100.0)
#     currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"])

#     category = st.selectbox(
#         "Expense Category",
#         ["Travel", "Food", "Accommodation", "Transportation", "Office Supplies", "Medical", "Other"]
#     )

#     manager_approval = st.selectbox(
#         "Manager Approval",
#         ["Not Provided", "Approved", "Rejected"]
#     )

#     description = st.text_area("Expense Description")

#     st.subheader("Supporting Documents")

#     uploaded_documents = st.file_uploader(
#         "Upload receipts, bills or invoices",
#         type=["pdf", "jpg", "jpeg", "png"],
#         accept_multiple_files=True
#     )

#     submitted = st.form_submit_button("Submit Expense")

# if submitted:
#     if not employee_name.strip():
#         st.error("Please enter the employee name.")
#     elif amount <= 0:
#         st.error("Please enter a valid expense amount.")
#     elif not uploaded_documents:
#         st.error("Please upload at least one supporting document.")
#     else:
#         approval_value = {
#             "Approved": True,
#             "Rejected": False,
#             "Not Provided": None
#         }[manager_approval]

#         employee_facts = {
#             "employee_name": employee_name.strip(),
#             "employee_id": employee_id.strip() or None,
#             "amount": Decimal(str(amount)),
#             "currency": currency,
#             "category": category,
#             "manager_approval": approval_value,
#             "description": description.strip() or None
#         }

#         uploaded_files = [
#             (file.name, file.getvalue())
#             for file in uploaded_documents
#         ]

#         try:
#             with st.spinner("Extracting documents and evaluating expense policies..."):
#                 result = process_expense(employee_facts, uploaded_files)

#             st.divider()
#             st.subheader("Expense Decision")

#             decision = result["decision"]

#             if decision == "APPROVE":
#                 st.success("Decision: APPROVE")
#             elif decision == "REJECT":
#                 st.error("Decision: REJECT")
#             else:
#                 st.warning("Decision: REQUIRES REVIEW")

#             st.markdown("**Decision Reason**")
#             st.write(result["decision_reason"])

#             st.markdown("**Missing Information**")
#             missing_information = result["missing_information"]

#             if missing_information:
#                 for item in missing_information:
#                     st.write(f"- {item}")
#             else:
#                 st.write("No missing information.")

#         except Exception as error:
#             st.error(f"Expense processing failed: {error}")




import streamlit as st
from decimal import Decimal
from reule_orchestrator import process_expense

st.set_page_config(
    page_title="AI Expense Decision Assistant",
    page_icon="💼",
    layout="centered"
)

st.title("AI Expense Decision Assistant")
st.caption("Intelligent expense validation and policy-based decision support")

with st.form("expense_form"):
    st.subheader("Employee Information")

    employee_name = st.text_input("Employee Name", placeholder="Enter employee name")
    employee_id = st.text_input("Employee ID", placeholder="Enter employee ID")

    st.subheader("Expense Details")

    amount = st.number_input(
        "Claim Amount",
        min_value=0.01,
        step=100.0,
        format="%.2f"
    )

    currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"])

    category = st.selectbox(
        "Expense Category",
        [
            "Travel",
            "Food",
            "Accommodation",
            "Transportation",
            "Office Supplies",
            "Medical",
            "Other"
        ]
    )

    manager_approval = st.selectbox(
        "Manager Approval",
        ["Not Provided", "Approved", "Rejected"]
    )

    description = st.text_area(
        "Expense Description",
        placeholder="Describe the purpose of the expense"
    )

    st.subheader("Supporting Documents")

    uploaded_documents = st.file_uploader(
        "Upload receipts, bills or invoices",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    submitted = st.form_submit_button(
        "Evaluate Expense",
        use_container_width=True
    )


if submitted:
    if not employee_name.strip():
        st.error("Please enter the employee name.")

    elif amount <= 0:
        st.error("Please enter a valid claim amount.")

    elif not uploaded_documents:
        st.error("Please upload at least one supporting document.")

    else:
        approval_mapping = {
            "Approved": True,
            "Rejected": False,
            "Not Provided": None
        }

        employee_facts = {
            "employee_name": employee_name.strip(),
            "employee_id": employee_id.strip() or None,
            "amount": Decimal(str(amount)),
            "currency": currency,
            "category": category,
            "manager_approval": approval_mapping[manager_approval],
            "description": description.strip() or None
        }

        uploaded_files = [
            (file.name, file.getvalue())
            for file in uploaded_documents
        ]

        try:
            with st.spinner(
                "Processing documents, retrieving policies and evaluating expense..."
            ):
                result = process_expense(employee_facts, uploaded_files)

            st.divider()
            st.subheader("Expense Decision")

            decision = result["decision"]

            if decision == "APPROVE":
                st.success("Decision: APPROVE")
            elif decision == "REJECT":
                st.error("Decision: REJECT")
            else:
                st.warning("Decision: REQUIRES REVIEW")

            st.markdown("### Decision Reason")
            st.write(result["decision_reason"])

            st.markdown("### Missing Information")

            missing_information = result.get("missing_information", [])

            if missing_information:
                for item in missing_information:
                    st.write(f"- {item}")
            else:
                st.write("No missing information identified.")

            st.markdown("### Policy Rules Used")

            policy_rules = result.get("policy_rules_used", [])

            if policy_rules:
                for rule in policy_rules:
                    st.write(f"- {rule}")
            else:
                st.write("No policy rules returned.")

            with st.expander("Technical Evaluation Details"):
                st.write("Rule Engine Status:", result.get("rule_status"))

            st.download_button(
                "Download Decision Report",
                data=__import__("json").dumps(result, indent=4, default=str),
                file_name="expense_decision.json",
                mime="application/json"
            )

        except Exception as error:
            st.error(f"Expense processing failed: {error}")
