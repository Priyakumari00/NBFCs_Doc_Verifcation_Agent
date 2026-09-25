from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from backend.agent_tools import (
    check_name_consistency,
    check_dob_consistency,
    check_required_documents,
    check_pan_format,
    check_account_number,
    check_ifsc_code
)

import os
from dotenv import load_dotenv

load_dotenv()


tools = [
    check_name_consistency,
    check_dob_consistency,
    check_required_documents,
    check_pan_format,
    check_account_number,
    check_ifsc_code,
]


model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)


agent = create_agent(
    model=model,
    tools=tools
)


def run_kyc_agent(
    aadhaar_data,
    pan_data,
    bank_data
):

    prompt = f"""
You are a KYC document verification agent.

Your task is to verify consistency between
Aadhaar, PAN and Bank Statement.

Use the available verification tools.

Do not make a loan approval or rejection decision.

Documents:

Aadhaar:
{aadhaar_data}

PAN:
{pan_data}

Bank Statement:
{bank_data}

Perform all appropriate verification checks.

Return the final result in exactly this format:

Verification Status: VERIFIED or NEEDS_REVIEW

Checks Performed:
- list each check and its result

Inconsistencies:
- list inconsistencies, or "None"

Reason:
- short explanation of the result

Important:
- Use VERIFIED only when all required documents are present and all relevant checks pass.
- Use NEEDS_REVIEW if any required document is missing or any verification check fails.
"""

    result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
})

    final_message = result["messages"][-1].content

    if isinstance(final_message, list):
     return final_message[0]["text"]

    return final_message

