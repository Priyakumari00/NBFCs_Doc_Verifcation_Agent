import re


def extract_bank_statement_data(text: str) -> dict:

    data = {
        "document_type": "bank_statement",
        "bank_name": None,
        "account_holder": None,
        "account_number": None,
        "ifsc_code": None,
        "opening_balance": None,
        "closing_balance": None,
        "transactions": []
    }

    text_upper = text.upper()

    # -------------------------
    # Bank Name
    # -------------------------

    bank_match = re.search(
        r"\bBANK\s*:\s*(.+)",
        text_upper
    )

    if bank_match:
        data["bank_name"] = bank_match.group(1).strip()

    # -------------------------
    # Account Holder
    # -------------------------

    holder_match = re.search(
        r"(?:ACCOUNT HOLDER|ACCOUNT NAME|CUSTOMER NAME)\s*:\s*(.+)",
        text_upper
    )

    if holder_match:
        data["account_holder"] = holder_match.group(1).strip()

    # -------------------------
    # Account Number
    # -------------------------

    account_match = re.search(
        r"(?:ACCOUNT NUMBER|A/C NUMBER|ACCOUNT NO\.?)\s*:\s*([0-9Xx\-]{6,20})",
        text_upper
    )

    if account_match:
        data["account_number"] = account_match.group(1)

    # -------------------------
    # IFSC
    # -------------------------

    ifsc_match = re.search(
        r"\bIFSC\s*:\s*([A-Z0-9]{4,15})",
        text_upper
    )

    if ifsc_match:
        data["ifsc_code"] = ifsc_match.group(1)

    # -------------------------
    # Opening Balance
    # -------------------------

    opening_match = re.search(
        r"OPENING BALANCE.*?([\d,]+\.\d{2})",
        text_upper
    )

    if opening_match:
        data["opening_balance"] = opening_match.group(1)

    # -------------------------
    # Transactions
    # -------------------------

    lines = [
        line.strip()
        for line in text_upper.splitlines()
        if line.strip()
    ]

    for line in lines:

        # Transaction date
        date_match = re.match(
            r"(\d{2}-[A-Z]{3}-\d{4})\s+(.+)",
            line
        )

        if not date_match:
            continue

        date = date_match.group(1)
        remaining = date_match.group(2)

        # Find all monetary values
        amounts = re.findall(
            r"\d[\d,]*\.\d{2}",
            remaining
        )

        if not amounts:
            continue

        # Remove amounts from description
        description = re.sub(
            r"\d[\d,]*\.\d{2}",
            "",
            remaining
        )

        description = description.replace("—", " ")
        description = description.replace("ZO", " ")
        description = " ".join(description.split())

        transaction = {
            "date": date,
            "description": description,
            "amounts": amounts
        }

        data["transactions"].append(transaction)

    # -------------------------
    # Closing Balance
    # -------------------------

    if data["transactions"]:
        last_transaction = data["transactions"][-1]

        if last_transaction["amounts"]:
            data["closing_balance"] = last_transaction["amounts"][-1]

    return data