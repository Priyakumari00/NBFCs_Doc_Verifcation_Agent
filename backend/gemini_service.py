import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()
# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_validation_results(validation_results):

    prompt = f"""
You are an AI assistant helping a human reviewer analyze
synthetic KYC document verification results.

Important rules:
- Do not approve or reject a loan.
- Do not make the final KYC decision.
- Only summarize the provided validation results.
- Clearly explain PASS and FAIL checks.
- If there are inconsistencies, explain exactly what differs.
- Keep the response concise and easy for a human reviewer to understand.

Validation results:

{json.dumps(validation_results, indent=2)}

Provide:

1. A short summary
2. The inconsistencies found
3. The checks that passed
4. A recommended next review step for the human reviewer
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text