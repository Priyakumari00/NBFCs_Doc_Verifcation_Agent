import os

from backend.ocr_service import (
    extract_text_from_pdf,
    extract_text_from_image
)

from backend.kyc_extractor import extract_kyc_data
from backend.bank_extractor import extract_bank_statement_data
from backend.document_integrity import analyze_document_integrity


def identify_document(text: str) -> str:

    text_upper = text.upper()

    # Aadhaar
    if "AADHAAR" in text_upper or "UIDAI" in text_upper:
        return "aadhaar"

    # PAN
    if (
        "INCOME TAX DEPARTMENT" in text_upper
        or "PAN" in text_upper
    ):
        return "pan"

    # Bank statement
    if (
        "BANK STATEMENT" in text_upper
        or "ACCOUNT NUMBER" in text_upper
        or "TRANSACTION" in text_upper
        or "IFSC" in text_upper
    ):
        return "bank_statement"

    return "unknown"


def process_document(file_path: str, expected_type: str | None = None) -> dict:

    extension = os.path.splitext(file_path)[1].lower()

    # OCR
    if extension == ".pdf":
        text = extract_text_from_pdf(file_path)

    elif extension in [".png", ".jpg", ".jpeg"]:
        text = extract_text_from_image(file_path)

    else:
        return {
            "error": "Unsupported file type"
        }

    # Identify document
    document_type = identify_document(text)

    # Extract structured data based on document type
    if document_type == "bank_statement":

        extracted_data = extract_bank_statement_data(text)

    else:

        extracted_data = extract_kyc_data(text)

    # Make sure detected document type is used
    extracted_data["document_type"] = document_type

    integrity = analyze_document_integrity(
        file_path,
        text,
        document_type,
        expected_type,
    )

    return {
        "document_type": document_type,
        "extracted_data": extracted_data,
        "raw_text": text,
        "integrity": integrity,
    }