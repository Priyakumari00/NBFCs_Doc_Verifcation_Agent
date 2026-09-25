from backend.kyc_agent import run_kyc_agent


aadhaar_data = {
    "name": "AARAV DEMO KUMAR",
    "date_of_birth": "01/01/1998"
}

pan_data = {
    "name": "AARAV DEMO KUMAR",
    "date_of_birth": "01/01/1998"
}

bank_data = {
    "account_holder": "AARAV DEMO KUMAR"
}


result = run_kyc_agent(
    aadhaar_data,
    pan_data,
    bank_data
)

print(result)