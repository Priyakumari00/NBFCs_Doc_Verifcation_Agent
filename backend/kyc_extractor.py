import re


def extract_kyc_data(text: str) -> dict:

    data = {
        "document_type": "unknown",
        "name": None,
        "date_of_birth": None,
        "gender": None,
        "address": None,
        "pan_number": None,
        "father_name": None
    }

    text_upper = text.upper()

    # -------------------------
    # Document type
    # -------------------------

    if "AADHAAR" in text_upper:
        data["document_type"] = "aadhaar"

    elif "INCOME TAX DEPARTMENT" in text_upper or "PAN" in text_upper:
        data["document_type"] = "pan"

    # -------------------------
    # PAN number
    # -------------------------

    pan_match = re.search(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        text_upper
    )

    if pan_match:
        data["pan_number"] = pan_match.group()

    # -------------------------
    # Date of Birth
    # -------------------------

    dob_match = re.search(
        r"(?:DATE OF BIRTH|DOB)\s*[:\-]?\s*"
        r"(\d{2}[/-]\d{2}[/-]\d{4})",
        text_upper
    )

    # Fallback: find any date
    if not dob_match:
        dob_match = re.search(
            r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",
            text_upper
        )

        if dob_match:
            data["date_of_birth"] = dob_match.group()

    else:
        data["date_of_birth"] = dob_match.group(1)

    # -------------------------
    # Gender
    # -------------------------

    if re.search(r"\bMALE\b", text_upper):
        data["gender"] = "Male"

    elif re.search(r"\bFEMALE\b", text_upper):
        data["gender"] = "Female"

    # -------------------------
    # Name
    # -------------------------

    name_match = re.search(
        r"\bNAME\s*[:\-]\s*([A-Z][A-Z]+(?:\s+[A-Z][A-Z]+){1,3})"
        r"(?=\s*(?:FATHER|DATE OF BIRTH|DOB|GENDER|ADDRESS|DEMO PAN|$))",
        text_upper
    )

    if name_match:
        data["name"] = name_match.group(1).strip()

    else:
        # Fallback for format:
        # Name Aarav Demo Kumar
        name_match = re.search(
            r"\bNAME\s+([A-Z][A-Z]+(?:\s+[A-Z][A-Z]+){1,3})"
            r"(?=\s*(?:FATHER|DATE OF BIRTH|DOB|GENDER|ADDRESS|DEMO PAN|$))",
            text_upper
        )

        if name_match:
            data["name"] = name_match.group(1).strip()

    # -------------------------
    # Father's Name
    # -------------------------

    father_match = re.search(
        r"(?:FATHER'S NAME|FATHER NAME)\s*[:\-]\s*"
        r"([A-Z][A-Z]+(?:\s+[A-Z][A-Z]+){1,3})"
        r"(?=\s*(?:DATE OF BIRTH|DOB|GENDER|ADDRESS|DEMO PAN|PAN|$))",
        text_upper
    )

    if father_match:
        data["father_name"] = father_match.group(1).strip()

    else:
        # Fallback for older OCR layout:
        # Father's Name
        # Date of Birth
        # ...
        # AARAV DEMO KUMAR
        # RAJESH DEMO KUMAR
        # 01/01/1995

        lines = [
            line.strip()
            for line in text_upper.splitlines()
            if line.strip()
        ]

        for i, line in enumerate(lines):

            if "FATHER'S NAME" in line or "FATHER NAME" in line:

                for j in range(i + 1, len(lines)):

                    if re.fullmatch(
                        r"\d{2}[/-]\d{2}[/-]\d{4}",
                        lines[j]
                    ):

                        if j - 1 > i:

                            candidate = lines[j - 1]

                            if candidate not in [
                                "DATE OF BIRTH",
                                "DEMO PAN",
                                "PAN",
                                "GENDER",
                                "ADDRESS"
                            ]:
                                data["father_name"] = candidate

                        break

    # -------------------------
    # Address
    # -------------------------

    address_match = re.search(
        r"\bADDRESS\s*(?:\([^)]*\))?\s*[:\-]?\s*(.+)",
        text_upper
    )

    if address_match:
        data["address"] = address_match.group(1).strip()

    return data