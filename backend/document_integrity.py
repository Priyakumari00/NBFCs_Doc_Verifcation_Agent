import hashlib
import os
import re
from pathlib import Path

import pymupdf
from PIL import Image, UnidentifiedImageError


MIN_OCR_CHARACTERS = 24
MIN_IMAGE_WIDTH = 300
MIN_IMAGE_HEIGHT = 200


def _check(name, status, message, severity=None):
    result = {
        "check": name,
        "status": status,
        "message": message,
    }

    if severity:
        result["severity"] = severity

    return result


def _file_sha256(file_path):
    digest = hashlib.sha256()

    with open(file_path, "rb") as document:
        for chunk in iter(lambda: document.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _ocr_checks(text):
    normalized_text = (text or "").strip()
    alphanumeric_count = len(re.findall(r"[A-Za-z0-9]", normalized_text))
    total_count = len(normalized_text)
    alphanumeric_ratio = (
        alphanumeric_count / total_count
        if total_count
        else 0
    )

    checks = []
    flags = []

    if len(normalized_text) < MIN_OCR_CHARACTERS:
        checks.append(_check(
            "OCR readability",
            "FLAG",
            "Very little text was extracted; the document may be blank, blurred, or unreadable.",
            "MEDIUM",
        ))
        flags.append({
            "type": "LOW_OCR_READABILITY",
            "severity": "MEDIUM",
            "message": "OCR extracted too little text to support reliable verification.",
        })
    else:
        checks.append(_check(
            "OCR readability",
            "PASS",
            "The document contains enough extracted text for automated checks.",
        ))

    if total_count and alphanumeric_ratio < 0.25:
        checks.append(_check(
            "OCR text quality",
            "FLAG",
            "Extracted content contains an unusually low proportion of letters and numbers.",
            "MEDIUM",
        ))
        flags.append({
            "type": "LOW_OCR_TEXT_QUALITY",
            "severity": "MEDIUM",
            "message": "OCR output is dominated by non-alphanumeric content.",
        })
    else:
        checks.append(_check(
            "OCR text quality",
            "PASS",
            "OCR output has a plausible text composition.",
        ))

    return checks, flags


def _pdf_checks(file_path):
    checks = []
    flags = []

    try:
        document = pymupdf.open(file_path)
        page_count = document.page_count

        if document.is_encrypted:
            checks.append(_check(
                "PDF encryption",
                "FLAG",
                "The PDF is encrypted and could not be independently inspected.",
                "HIGH",
            ))
            flags.append({
                "type": "ENCRYPTED_DOCUMENT",
                "severity": "HIGH",
                "message": "Encrypted documents require manual review.",
            })
        else:
            checks.append(_check(
                "PDF structure",
                "PASS" if page_count > 0 else "FLAG",
                "PDF structure is readable." if page_count > 0 else "The PDF has no readable pages.",
                None if page_count > 0 else "HIGH",
            ))

            if page_count == 0:
                flags.append({
                    "type": "EMPTY_DOCUMENT",
                    "severity": "HIGH",
                    "message": "The PDF contains no readable pages.",
                })

        document.close()
    except Exception as error:
        checks.append(_check(
            "PDF structure",
            "FLAG",
            f"The PDF could not be inspected: {error}",
            "HIGH",
        ))
        flags.append({
            "type": "MALFORMED_DOCUMENT",
            "severity": "HIGH",
            "message": "The uploaded PDF could not be opened safely.",
        })

    return checks, flags


def _image_checks(file_path):
    checks = []
    flags = []

    try:
        with Image.open(file_path) as image:
            width, height = image.size
            image.verify()

        if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
            checks.append(_check(
                "Image resolution",
                "FLAG",
                "Image resolution is too low for dependable document review.",
                "MEDIUM",
            ))
            flags.append({
                "type": "LOW_IMAGE_RESOLUTION",
                "severity": "MEDIUM",
                "message": "The image may not contain enough detail for reliable verification.",
            })
        else:
            checks.append(_check(
                "Image resolution",
                "PASS",
                "Image resolution is sufficient for automated review.",
            ))
    except (UnidentifiedImageError, OSError) as error:
        checks.append(_check(
            "Image structure",
            "FLAG",
            f"The image could not be inspected: {error}",
            "HIGH",
        ))
        flags.append({
            "type": "MALFORMED_DOCUMENT",
            "severity": "HIGH",
            "message": "The uploaded image could not be opened safely.",
        })

    return checks, flags


def analyze_document_integrity(file_path, text, detected_type, expected_type=None):
    extension = Path(file_path).suffix.lower()
    checks, flags = _ocr_checks(text)

    if extension == ".pdf":
        structure_checks, structure_flags = _pdf_checks(file_path)
    elif extension in {".png", ".jpg", ".jpeg"}:
        structure_checks, structure_flags = _image_checks(file_path)
    else:
        structure_checks = [_check(
            "File type",
            "FLAG",
            "Unsupported document file type.",
            "HIGH",
        )]
        structure_flags = [{
            "type": "UNSUPPORTED_FILE_TYPE",
            "severity": "HIGH",
            "message": "The uploaded file type is not supported for verification.",
        }]

    checks.extend(structure_checks)
    flags.extend(structure_flags)

    if expected_type and detected_type != expected_type:
        checks.append(_check(
            "Document type",
            "FLAG",
            f"Expected {expected_type}, but OCR identified {detected_type}.",
            "HIGH",
        ))
        flags.append({
            "type": "DOCUMENT_TYPE_MISMATCH",
            "severity": "HIGH",
            "message": f"Expected {expected_type}, but detected {detected_type}.",
        })
    else:
        checks.append(_check(
            "Document type",
            "PASS",
            f"Document identified as {detected_type}.",
        ))

    file_size = os.path.getsize(file_path)

    return {
        "sha256": _file_sha256(file_path),
        "file_size": file_size,
        "extension": extension,
        "checks": checks,
        "risk_flags": flags,
        "status": "FLAGGED" if flags else "PASS",
    }
