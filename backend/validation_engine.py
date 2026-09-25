import re


def validate_pan(pan_number):
    """
    Validate Indian PAN format:
    5 letters + 4 digits + 1 letter
    Example: ABCDE1234F
    """

    if not pan_number:
        return False

    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

    return bool(
        re.fullmatch(pattern, pan_number.upper())
    )


def validate_ifsc(ifsc_code):
    """
    Validate basic IFSC structure:
    4 letters + 0 + 6 alphanumeric characters
    Example: SBIN0001234
    """

    if not ifsc_code:
        return False

    pattern = r"^[A-Z]{4}0[A-Z0-9]{6}$"

    return bool(
        re.fullmatch(pattern, ifsc_code.upper())
    )


def validate_account_number(account_number):
    """
    Basic bank account number validation.
    Allows 9-18 digits.
    """

    if not account_number:
        return False

    account_number = str(account_number).replace(" ", "")

    return bool(
        re.fullmatch(r"\d{9,18}", account_number)
    )


def check_document_completeness(
    aadhaar_data,
    pan_data,
    bank_data
):

    results = []
    missing_documents = []

    documents = {
        "Aadhaar": aadhaar_data,
        "PAN": pan_data,
        "Bank Statement": bank_data
    }

    for document_name, document_data in documents.items():

        if (
            document_data
            and document_data.get("document_type") != "unknown"
        ):

            results.append({
                "document": document_name,
                "status": "PRESENT"
            })

        else:

            results.append({
                "document": document_name,
                "status": "MISSING"
            })

            missing_documents.append(document_name)

    return {
        "required_documents": len(documents),
        "present_documents": (
            len(documents) - len(missing_documents)
        ),
        "missing_documents": missing_documents,
        "status": (
            "COMPLETE"
            if not missing_documents
            else "INCOMPLETE"
        ),
        "documents": results
    }


def validate_documents(
    aadhaar_data,
    pan_data,
    bank_data,
    integrity_results=None,
):

    results = []
    risk_flags = []
    integrity_results = integrity_results or {}

    # --------------------------------------------------
    # 1. DOCUMENT COMPLETENESS
    # --------------------------------------------------

    completeness = check_document_completeness(
        aadhaar_data,
        pan_data,
        bank_data
    )

    if completeness["status"] == "INCOMPLETE":

        risk_flags.append({
            "type": "MISSING_DOCUMENT",
            "severity": "MEDIUM",
            "message": "One or more required documents are missing"
        })

    # --------------------------------------------------
    # 2. DOCUMENT INTEGRITY AND READABILITY
    # --------------------------------------------------

    for document_name, integrity in integrity_results.items():
        for check in integrity.get("checks", []):
            results.append({
                "check": f"{document_name}: {check['check']}",
                "status": "PASS" if check["status"] == "PASS" else "FAIL",
                "message": check["message"],
            })

        risk_flags.extend(
            {
                **flag,
                "document": document_name,
            }
            for flag in integrity.get("risk_flags", [])
        )

    # --------------------------------------------------
    # 3. NAME MATCH: AADHAAR VS PAN
    # --------------------------------------------------

    aadhaar_name = aadhaar_data.get("name")
    pan_name = pan_data.get("name")

    if aadhaar_name and pan_name:

        if aadhaar_name.upper() == pan_name.upper():

            results.append({
                "check": "Name Match: Aadhaar vs PAN",
                "status": "PASS",
                "message": "Name matches"
            })

        else:

            results.append({
                "check": "Name Match: Aadhaar vs PAN",
                "status": "FAIL",
                "message": "Name does not match"
            })

            risk_flags.append({
                "type": "NAME_MISMATCH",
                "severity": "HIGH",
                "message": "Name differs between Aadhaar and PAN"
            })

    # --------------------------------------------------
    # 4. NAME MATCH: PAN VS BANK
    # --------------------------------------------------

    bank_name = bank_data.get("account_holder")

    if pan_name and bank_name:

        if pan_name.upper() == bank_name.upper():

            results.append({
                "check": "Name Match: PAN vs Bank",
                "status": "PASS",
                "message": "Name matches"
            })

        else:

            results.append({
                "check": "Name Match: PAN vs Bank",
                "status": "FAIL",
                "message": "Name does not match"
            })

            risk_flags.append({
                "type": "NAME_MISMATCH",
                "severity": "HIGH",
                "message": "Name differs between PAN and bank statement"
            })

    # --------------------------------------------------
    # 5. DOB MATCH
    # --------------------------------------------------

    aadhaar_dob = aadhaar_data.get("date_of_birth")
    pan_dob = pan_data.get("date_of_birth")

    if aadhaar_dob and pan_dob:

        if aadhaar_dob == pan_dob:

            results.append({
                "check": "DOB Match: Aadhaar vs PAN",
                "status": "PASS",
                "message": "Date of birth matches"
            })

        else:

            results.append({
                "check": "DOB Match: Aadhaar vs PAN",
                "status": "FAIL",
                "message": "Date of birth does not match"
            })

            risk_flags.append({
                "type": "DOB_MISMATCH",
                "severity": "HIGH",
                "message": "Date of birth differs between Aadhaar and PAN"
            })

    # --------------------------------------------------
    # 6. PAN FORMAT
    # --------------------------------------------------

    pan_number = pan_data.get("pan_number")

    if pan_number:

        if validate_pan(pan_number):

            results.append({
                "check": "PAN Format",
                "status": "PASS",
                "message": "PAN format is valid"
            })

        else:

            results.append({
                "check": "PAN Format",
                "status": "FAIL",
                "message": "PAN format is invalid"
            })

            risk_flags.append({
                "type": "INVALID_PAN_FORMAT",
                "severity": "MEDIUM",
                "message": "PAN does not match the expected format"
            })

    else:

        results.append({
            "check": "PAN Format",
            "status": "FAIL",
            "message": "PAN number missing"
        })

        risk_flags.append({
            "type": "MISSING_PAN",
            "severity": "MEDIUM",
            "message": "PAN number could not be extracted"
        })

    # --------------------------------------------------
    # 7. BANK ACCOUNT NUMBER
    # --------------------------------------------------

    account_number = bank_data.get("account_number")

    if account_number:

        if validate_account_number(account_number):

            results.append({
                "check": "Bank Account Number",
                "status": "PASS",
                "message": "Bank account number has a valid basic format"
            })

        else:

            results.append({
                "check": "Bank Account Number",
                "status": "FAIL",
                "message": "Bank account number format looks invalid"
            })

            risk_flags.append({
                "type": "INVALID_BANK_ACCOUNT",
                "severity": "MEDIUM",
                "message": "Bank account number does not match the expected numeric format"
            })

    else:

        results.append({
            "check": "Bank Account Number",
            "status": "FAIL",
            "message": "Account number missing"
        })

        risk_flags.append({
            "type": "MISSING_BANK_ACCOUNT",
            "severity": "MEDIUM",
            "message": "Bank account number could not be extracted"
        })

    # --------------------------------------------------
    # 8. IFSC FORMAT
    # --------------------------------------------------

    ifsc_code = bank_data.get("ifsc_code")

    if ifsc_code:

        if validate_ifsc(ifsc_code):

            results.append({
                "check": "IFSC Code",
                "status": "PASS",
                "message": "IFSC format is valid"
            })

        else:

            results.append({
                "check": "IFSC Code",
                "status": "FAIL",
                "message": "IFSC format is invalid"
            })

            risk_flags.append({
                "type": "INVALID_IFSC",
                "severity": "MEDIUM",
                "message": "IFSC code does not match the expected format"
            })

    else:

        results.append({
            "check": "IFSC Code",
            "status": "FAIL",
            "message": "IFSC code missing"
        })

        risk_flags.append({
            "type": "MISSING_IFSC",
            "severity": "MEDIUM",
            "message": "IFSC code could not be extracted"
        })

    # --------------------------------------------------
    # 9. SUMMARY
    # --------------------------------------------------

    passed = sum(
        1
        for result in results
        if result["status"] == "PASS"
    )

    failed = sum(
        1
        for result in results
        if result["status"] == "FAIL"
    )

    # --------------------------------------------------
    # 10. RISK COUNTS
    # --------------------------------------------------

    high_risk = sum(
        1
        for flag in risk_flags
        if flag["severity"] == "HIGH"
    )

    medium_risk = sum(
        1
        for flag in risk_flags
        if flag["severity"] == "MEDIUM"
    )

    # --------------------------------------------------
    # 11. REVIEW PRIORITY
    # --------------------------------------------------

    if high_risk > 0:

        review_priority = "HIGH"

    elif medium_risk > 0:

        review_priority = "MEDIUM"

    else:

        review_priority = "LOW"

    # --------------------------------------------------
    # 12. FINAL RESULT
    # --------------------------------------------------

    return {

        "document_completeness": completeness,

        "summary": {
            "total_checks": len(results),
            "passed": passed,
            "failed": failed
        },

        "review_priority": review_priority,

        "risk_flags": risk_flags,

        "checks": results
    }