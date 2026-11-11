
import os
import json
import time
import base64
from io import BytesIO

from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = OpenAI(
    base_url=os.getenv("VLM_API_ENDPOINT"),
    api_key=os.getenv("VLM_API_TOKEN")
)

MODEL_NAME = os.getenv("VLM_MODEL_NAME")


EXTRACTION_PROMPT = """
You are an expert financial and expense document understanding AI.

Your task is to visually inspect the provided receipt or bill and extract
the actual information printed in the document.

Do not describe the extraction task. Do not repeat these instructions.
You MUST inspect the image and extract its contents.

Return a JSON object with exactly these fields:

{
    "vendor_name": null,
    "document_type": null,
    "receipt_number": null,
    "transaction_date": null,
    "total_amount": null,
    "total_paid": null,
    "currency": null,
    "tax_amount": null,
    "expense_category": null,
    "description": null,
    "line_items": [],
    "confidence": "low",
    "evidence": []
}

Extraction instructions:

1. Extract the actual vendor or organization name.
2. Identify whether the document is a receipt, invoice, hospital bill,
   money receipt or another financial document.
3. Extract receipt, invoice or bill number when available.
4. Extract the relevant transaction or bill date.
5. Extract the final bill amount separately from the amount paid.
6. Extract tax only when explicitly mentioned.
7. Identify the expense category from the document.
8. Extract individual services or purchased items into line_items.
9. Do not confuse advance payments, total bill, total paid and refundable amount.
10. Preserve the original numerical values.
11. Use null for information that is not available.
12. Include short evidence from the document.
13. Confidence must be high, medium or low.
14. Never invent information.

Return only the extracted JSON object.
"""


def encode_pil_image(image):
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def ask_vlm(image=None, prompt=EXTRACTION_PROMPT, max_retries=3):

    last_error = None

    for attempt in range(max_retries):
        try:
            content = [{"type": "text", "text": prompt}]

            if image is not None:
                base64_image = encode_pil_image(image.convert("RGB"))

                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            response = _client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0.1,
                max_tokens=2048,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert financial document understanding AI. Always inspect the provided document and extract its actual information."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )

            result = response.choices[0].message.content

            if not result:
                raise ValueError("VLM returned an empty response")

            result = json.loads(result)

            required_fields = {
                "vendor_name",
                "document_type",
                "receipt_number",
                "transaction_date",
                "total_amount",
                "total_paid",
                "currency",
                "tax_amount",
                "expense_category",
                "description",
                "line_items",
                "confidence",
                "evidence"
            }

            if not isinstance(result, dict) or not required_fields.issubset(result):
                raise ValueError(f"Invalid extraction response. Returned keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")

            return result

        except Exception as e:
            last_error = e

            print(f"VLM request failed (attempt {attempt + 1}/{max_retries}): {e}")

            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))

    raise last_error


def extract_page_facts(page):

    if page["content_type"] == "text":
        prompt = (
            EXTRACTION_PROMPT
            + "\n\nDocument text:\n"
            + page["content"]
        )

        return ask_vlm(prompt=prompt)

    image_data = page["content"].split(",", 1)[1]
    image_bytes = base64.b64decode(image_data)

    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    return ask_vlm(image=image)


def extract_document_facts(document):

    extracted_pages = []

    for page in document["pages"]:
        facts = extract_page_facts(page)

        extracted_pages.append({
            "page_number": page["page_number"],
            "facts": facts
        })

    return {
        "filename": document["filename"],
        "extracted_pages": extracted_pages
    }
