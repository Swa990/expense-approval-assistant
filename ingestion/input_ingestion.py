import fitz
import base64
from io import BytesIO


SUPPORTED_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png"
}


def encode_image(image_bytes, mime_type):
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def ingest_document(filename, file_bytes):
    extension = filename.lower().rsplit(".", 1)[-1]
    extension = f".{extension}"

    if extension not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file format: {extension}")

    pages = []

    if extension == ".pdf":
        document = fitz.open(stream=file_bytes, filetype="pdf")

        for page_number, page in enumerate(document):
            text = page.get_text("text").strip()

            if len(text) >= 40:
                pages.append({
                    "page_number": page_number + 1,
                    "content_type": "text",
                    "content": text
                })
            else:
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image_bytes = pixmap.tobytes("png")

                pages.append({
                    "page_number": page_number + 1,
                    "content_type": "image",
                    "content": encode_image(image_bytes, "image/png")
                })

        document.close()

    else:
        pages.append({
            "page_number": 1,
            "content_type": "image",
            "content": encode_image(file_bytes, SUPPORTED_TYPES[extension])
        })

    return {
        "filename": filename,
        "pages": pages
    }