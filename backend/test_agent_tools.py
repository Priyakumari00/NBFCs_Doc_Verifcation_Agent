from backend.agent_tools import (
    check_name_consistency,
    check_dob_consistency,
    check_required_documents,
    check_pan_format,
    check_account_number,
    check_ifsc_code
)


result = check_name_consistency.invoke({
    "aadhaar_name": "AARAV DEMO KUMAR",
    "pan_name": "AARAV DEMO KUMAR",
    "bank_name": "AARAV DEMO KUMAR"
})

print(result)


result = check_dob_consistency.invoke({
    "aadhaar_dob": "01/01/1998",
    "pan_dob": "01/01/1998"
})

print(result)


result = check_required_documents.invoke({
    "aadhaar_present": True,
    "pan_present": True,
    "bank_present": True
})

print(result)

result = check_pan_format.invoke({
    "pan_number": "DEMOP1234X"
})

print(result)

result = check_account_number.invoke({
    "account_number": "000000000000"
})

print(result)

result = check_ifsc_code.invoke({
    "ifsc_code": "DEMO0000000"
})

print(result)