from langchain_core.tools import tool


@tool
def check_name_consistency(
    aadhaar_name: str,
    pan_name: str,
    bank_name: str
) -> dict:
    """
    Compare the person's name across Aadhaar, PAN,
    and bank statement.
    """

    results = []

    if aadhaar_name.upper() == pan_name.upper():
        aadhaar_pan = "PASS"
    else:
        aadhaar_pan = "FAIL"

    if pan_name.upper() == bank_name.upper():
        pan_bank = "PASS"
    else:
        pan_bank = "FAIL"

    results.append({
        "check": "Aadhaar vs PAN Name",
        "status": aadhaar_pan
    })

    results.append({
        "check": "PAN vs Bank Name",
        "status": pan_bank
    })

    return {
        "results": results,
        "all_match": (
            aadhaar_pan == "PASS"
            and pan_bank == "PASS"
        )
    }


@tool
def check_dob_consistency(
    aadhaar_dob: str,
    pan_dob: str
) -> dict:
    """
    Compare date of birth between Aadhaar and PAN.
    """

    matches = aadhaar_dob == pan_dob

    return {
        "check": "Aadhaar vs PAN DOB",
        "status": "PASS" if matches else "FAIL",
        "matches": matches
    }


@tool
def check_required_documents(
    aadhaar_present: bool,
    pan_present: bool,
    bank_present: bool
) -> dict:
    """
    Check whether all required KYC documents are present.
    """

    missing = []

    if not aadhaar_present:
        missing.append("Aadhaar")

    if not pan_present:
        missing.append("PAN")

    if not bank_present:
        missing.append("Bank Statement")

    return {
        "status": "COMPLETE" if not missing else "INCOMPLETE",
        "missing_documents": missing
    }

@tool
def check_pan_format(pan_number: str) -> dict:
    """
    Check whether a PAN number follows the expected format.
    """

    import re

    if not pan_number:
        return {
            "check": "PAN Format",
            "status": "FAIL",
            "message": "PAN number is missing"
        }

    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

    is_valid = bool(
        re.fullmatch(pattern, pan_number.upper())
    )

    return {
        "check": "PAN Format",
        "status": "PASS" if is_valid else "FAIL",
        "message": (
            "PAN format is valid"
            if is_valid
            else "PAN format is invalid"
        )
    }

@tool
def check_account_number(account_number: str) -> dict:
    """
    Check whether a bank account number follows
    the expected basic numeric format.
    """

    if not account_number:
        return {
            "check": "Bank Account Number",
            "status": "FAIL",
            "message": "Account number is missing"
        }

    account_number = str(account_number).replace(" ", "")

    import re

    is_valid = bool(
        re.fullmatch(r"\d{9,18}", account_number)
    )

    return {
        "check": "Bank Account Number",
        "status": "PASS" if is_valid else "FAIL",
        "message": (
            "Bank account number has a valid basic format"
            if is_valid
            else "Bank account number format looks invalid"
        )
    }

@tool
def check_ifsc_code(ifsc_code: str) -> dict:
    """
    Check whether an IFSC code follows the expected basic format.
    """

    if not ifsc_code:
        return {
            "check": "IFSC Code",
            "status": "FAIL",
            "message": "IFSC code is missing"
        }

    import re

    is_valid = bool(
        re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", ifsc_code.upper())
    )

    return {
        "check": "IFSC Code",
        "status": "PASS" if is_valid else "FAIL",
        "message": (
            "IFSC format is valid"
            if is_valid
            else "IFSC format is invalid"
        )
    }