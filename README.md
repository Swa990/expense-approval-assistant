# AI Expense Decision Assistant

An AI-powered expense evaluation system that analyzes employee expense claims, extracts information from supporting documents, retrieves relevant company policies, and evaluates expenses using two different validation approaches: **LLM-Based Validation** and **Python-Based Validation**.

## Live Application

**Try the application:** [AI Expense Decision Assistant](https://expense-approval-assistant-paep5mt9hclqqb4vt7ksiv.streamlit.app/)

## 1. Problem Statement

Organizations receive expense claims from employees along with supporting documents such as receipts, invoices, and bills.

Manually reviewing every expense is time-consuming. It also becomes difficult to maintain consistent decisions when multiple policies, approval conditions, and supporting documents are involved.

The objective of this project is to build an AI-assisted expense decision system that can:

- Understand employee expense information.
- Extract relevant information from uploaded PDF and image documents.
- Retrieve relevant company expense policies.
- Compare submitted information against policy requirements.
- Identify missing information, policy violations, and exceptions.
- Generate an explainable expense decision.

The system provides three possible decisions:

- **APPROVE:** The expense satisfies the evaluated requirements.
- **REJECT:** The expense violates an applicable policy condition.
- **REQUIRES REVIEW:** More information or manual verification is necessary.

The application also provides two evaluation approaches so their processing behavior and results can be compared.

## 2. Solution Overview

The system follows a structured workflow:

1. Employee submits expense information and supporting documents.
2. The documents are processed and relevant information is extracted.
3. The expense policy knowledge base is searched using RAG.
4. Extracted facts are compared with the relevant policy conditions.
5. The selected validation approach evaluates the expense.
6. The system returns a decision, explanation, and missing information.

Instead of relying on a single LLM prompt to decide whether an expense should be approved, the project explores two approaches to expense validation.

## 3. Two Evaluation Approaches

The application allows users to select their preferred evaluation method before submitting an expense.

### Approach 1: LLM-Based Validation

In this approach, the LLM is used for document understanding, fact validation, policy interpretation, and decision generation.

**Workflow:**

1. Extract information from the uploaded documents using a Vision Language Model.
2. Retrieve relevant policy information from the FAISS knowledge base.
3. Prepare the employee information, extracted document facts, and retrieved policy context.
4. Pass the combined information to the LLM validator.
5. Validate the returned structured response.
6. Display the final decision and explanation.

This approach uses the language model to interpret the relationship between expense information and policy conditions.

**Observed processing time: Approximately 15 seconds.**

### Approach 2: Python-Based Validation

In this approach, the decision-making process is handled through deterministic Python logic rather than asking an LLM to make the final decision.

**Workflow:**

1. Extract information from the uploaded documents.
2. Retrieve relevant expense policies using FAISS.
3. Validate the extracted facts.
4. Apply Python-based policy rules.
5. Identify policy violations, missing information, and exceptions.
6. Generate the final decision using the rule engine.

The decision is based on explicit conditions and comparisons rather than an LLM-generated recommendation.

**Observed processing time: Approximately 10 seconds.**

### Comparison

| Criteria | LLM-Based Validation | Python-Based Validation |
|---|---|---|
| Decision approach | LLM interpretation | Deterministic Python rules |
| Policy interpretation | LLM-based | Rule-based |
| Fact validation | LLM-assisted | Python-based |
| Decision generation | LLM | Python |
| Output | Structured decision and explanation | Structured decision and explanation |
| Observed processing time | ~15 seconds | ~10 seconds |

*Processing times are approximate observations from application testing, not formal performance benchmarks. Actual times may vary depending on document size, API response time, and retrieval operations.*

## 4. Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Programming Language | Python |
| Document Processing | PyMuPDF |
| Image Processing | Pillow |
| Document Understanding | Vision Language Model |
| LLM Integration | OpenAI-compatible API |
| Embedding Model | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Database | FAISS |
| Retrieval Approach | Retrieval-Augmented Generation (RAG) |
| Data Validation | Pydantic |
| Decision Engine | Python Rule Engine |

## 5. System Architecture

```text
                  EMPLOYEE
                     |
                     v
          Streamlit Expense Application
                     |
                     v
             Employee Information
             + Supporting Documents
                     |
                     v
             Document Ingestion
                     |
          +----------+----------+
          |                     |
          v                     v
     Text-based PDF       Image / Scanned PDF
          |                     |
          v                     v
     Text Extraction       VLM Processing
          |                     |
          +----------+----------+
                     |
                     v
             Fact Extraction
                     |
                     v
              Policy Retrieval
                     |
                     v
             FAISS Vector Index
                     |
                     v
          Relevant Policy Context
                     |
                     v
             Evaluation Selection
                     |
              +------+------+
              |             |
              v             v
          LLM-Based      Python-Based
          Validation     Validation
              |             |
              v             v
          LLM Decision   Rule Engine
              |             |
              +------+------+
                     |
                     v
              Final Decision
                     |
                     v
          Decision + Explanation
          + Missing Information
```

## 6. Retrieval-Augmented Generation (RAG)

The system uses RAG to retrieve relevant expense policies instead of relying entirely on information provided in an LLM prompt.

### Policy Ingestion

The policy documents are processed during ingestion.

The process includes:

1. Reading policy documents.
2. Splitting documents into smaller text chunks.
3. Generating embeddings using Sentence Transformers.
4. Storing the vectors in a FAISS index.

### Policy Retrieval

When an expense is submitted:

1. The expense information is used to formulate a retrieval query.
2. The query is converted into an embedding.
3. FAISS searches for relevant policy chunks.
4. Retrieved policy information is provided to the selected validation workflow.

This allows the system to use relevant policy information during expense evaluation.

### Why RAG?

- Policies can be maintained separately from application code.
- Relevant policy information can be retrieved dynamically.
- The system can work with multiple policy documents.
- The LLM receives relevant context instead of requiring the entire policy document in every request.

## 7. Policy Rule Engine

The Python-based rule engine evaluates expense information against retrieved policy conditions.

Some of the conditions considered include:

- Expense amount against the applicable policy limit.
- Manager approval requirements.
- Availability of supporting documents.
- Missing or unreadable documents.
- Missing transaction information.
- Differences between the claimed amount and receipt amount.
- Unknown or ambiguous policy conditions.
- Duplicate document or receipt information.

The engine separates different types of findings:

| Finding | Meaning |
|---|---|
| Policy violation | A condition explicitly violates an applicable policy |
| Missing information | Required information is unavailable |
| Unknown condition | The system cannot confidently evaluate a condition |
| Exception | A situation requiring additional verification |

This separation helps prevent missing information from automatically being treated as a policy violation.

## 8. Document Processing

The application supports the following uploaded document formats:

- PDF
- JPG
- JPEG
- PNG

The document ingestion process handles text-based PDFs and scanned documents.

For text-based PDFs, text is extracted directly.

For scanned PDFs and images, document pages are processed as images and passed through the Vision Language Model for information extraction.

The extracted information can include:

- Document type
- Vendor information
- Receipt number
- Transaction date
- Total amount
- Currency
- Tax information
- Expense category
- Description
- Line items
- Extraction confidence
- Supporting evidence

The extracted facts are then used during expense validation.

## 9. Application Features

- Employee information submission.
- Expense amount and currency selection.
- Expense category selection.
- Manager approval information.
- Expense description.
- Multiple document uploads.
- LLM-based validation option.
- Python-based validation option.
- Decision explanation.
- Missing information reporting.
- Processing time measurement.
- Downloadable JSON decision report.

## 10. Project Structure

```text
expense_approval_system/
│
├── app.py
├── orchestrator.py
├── rule_orchestrator.py
│
├── schemas/
│   └── expense_schema.py
│
├── ingestion/
│   └── document_ingestion.py
│
├── extraction/
│   └── fact_extractor.py
│
├── rag/
│   ├── policy_ingestion.py
│   └── policy_retriever.py
│
├── policies/
│   └── expense_reimbursement_policy.md
│
├── knowledge_base/
│   └── faiss_index/
│
├── decision/
│   ├── policy_rule_engine.py
│   └── llm_reasoner.py
│
├── validation/
│   └── fact_validator.py
│
├── requirements.txt
├── .env.example
└── README.md
```

*The structure above describes the main application components. Some supporting files and configuration files may differ in the deployed version.*

## 11. Installation and Setup

### Prerequisites

- Python 3.10 or later.
- Git.
- Access to the configured LLM/VLM API.
- Required API credentials.

### Clone the repository

```bash
git clone https://github.com/Swa990/expense-approval-assistant.git

cd expense-approval-assistant
```

### Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file using `.env.example` as a reference.

Configure the required API settings:

```env
VLM_API_ENDPOINT=your_api_endpoint
VLM_API_TOKEN=your_api_token
VLM_MODEL_NAME=your_model_name
```

Do not commit the `.env` file or expose API credentials in the repository.

### Prepare the FAISS knowledge base

Run the policy ingestion process to generate the FAISS index if it is not already available.

Use the project's policy ingestion module and ensure the generated index is stored in:

```text
knowledge_base/faiss_index/
```

If the repository includes a compatible prebuilt index, use that index instead of rebuilding it.

### Run the application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

## 12. Example Usage

Consider the following expense submission:

| Field | Value |
|---|---|
| Employee Name | Rahul |
| Expense Amount | ₹42,000 |
| Expense Category | Travel |
| Manager Approval | Approved |
| Supporting Receipt | Available |
| Travel Policy Limit | ₹25,000 |

The system retrieves the relevant travel policy and evaluates the claim.

Since the submitted amount exceeds the stated travel limit, the expense requires the additional approval specified by the policy.

The system should identify the applicable requirement and return an appropriate decision based on the available information.

This example illustrates why expense evaluation must consider both employee-submitted facts and policy conditions.

## 13. Testing and Evaluation

The application was tested using both validation approaches.

The evaluation focuses on:

- Correct extraction of information from uploaded documents.
- Correct retrieval of relevant policy information.
- Accurate comparison of expense facts against policy conditions.
- Identification of missing information.
- Identification of policy violations.
- Consistency of structured decision output.
- Handling of incomplete or ambiguous documents.
- Processing time of each approach.

### Performance Observations

| Evaluation approach | Observed processing time |
|---|---:|
| LLM-Based Validation | ~15 seconds |
| Python-Based Validation | ~10 seconds |

These are observed application timings and should not be interpreted as statistically validated performance results.

## 14. Design Decisions

### Why use two validation approaches?

The project explores two ways of solving the same decision-making problem.

**LLM-based validation** can interpret contextual information and reason about policy language.

**Python-based validation** provides explicit, reproducible decision conditions and avoids relying on an LLM to make the final decision.

Keeping both approaches available makes it possible to compare their decisions, processing time, and behavior on different expense scenarios.

### Why use RAG?

Company policies may change over time. Keeping policy information in a separate knowledge base makes it easier to update and retrieve relevant rules without embedding every policy condition directly into application prompts or source code.

### Why use a rule engine?

Expense decisions often depend on explicit conditions such as limits, approvals, and required documents.

These conditions are more suitable for deterministic evaluation, where the system can identify exactly which condition was satisfied or violated.

## 15. Future Improvements

Potential improvements include:

- Add OCR-based PII detection and image masking before sending sensitive documents to external VLM APIs.
- Implement stronger role-based access control.
- Add encryption for stored documents and extracted employee information.
- Improve duplicate receipt detection using document hashes and additional identifiers.
- Add retrieval caching and metadata filtering for larger policy knowledge bases.
- Add more comprehensive automated test cases.
- Measure decision accuracy, extraction accuracy, retrieval quality, and latency across a larger test dataset.
- Introduce detailed audit trails for expense decisions.
- Improve handling of handwritten and low-quality scanned documents.

## 16. Security and Data Privacy

Expense documents may contain personal and financial information.

The application should be deployed with appropriate security controls.

Important considerations include:

- Keep API credentials in environment variables or a secret manager.
- Never commit `.env` files.
- Restrict access to uploaded employee documents.
- Protect the FAISS index and stored data.
- Avoid exposing sensitive information in application logs.
- Verify the data-retention and privacy policies of external model providers.

PII masking, image sanitization, and additional access-control measures are identified as security improvements and should not be considered implemented unless explicitly enabled in the application.

## 17. Live Demo

The application is deployed using Streamlit Community Cloud.

**Live Application:**

[AI Expense Decision Assistant](https://expense-approval-assistant-paep5mt9hclqqb4vt7ksiv.streamlit.app/)

## 18. Conclusion

The AI Expense Decision Assistant demonstrates how LLMs, document understanding, Retrieval-Augmented Generation, and deterministic Python logic can work together to support expense evaluation.

The project explores two different validation strategies:

1. Using an LLM to interpret facts and policies and generate a decision.
2. Using Python-based validation and explicit policy rules to generate a decision.

By providing both approaches in one application, the system makes it possible to compare their reasoning behavior, decision outcomes, and processing time.

The overall objective is to make expense evaluation more structured, explainable, and consistent while reducing the amount of manual effort required.
