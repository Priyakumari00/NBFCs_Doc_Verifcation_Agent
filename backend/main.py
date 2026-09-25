from fastapi import FastAPI, UploadFile, File
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from uuid import uuid4

from backend.ocr_service import extract_text_from_pdf, extract_text_from_image
from backend.kyc_extractor import extract_kyc_data
from backend.document_processor import process_document
from backend.validation_engine import validate_documents
from backend.gemini_service import analyze_validation_results
from backend.verification_report import generate_verification_report
from backend.agent_decision import make_verification_decision
from backend.kyc_agent import run_kyc_agent


app = FastAPI(
    title="AI Document Verification Agent",
    description="AI-powered document verification system for NBFC workflows",
    version="1.0.0"
)


# ---------------------------------
# CORS
# ---------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_upload(file: UploadFile) -> tuple[Path, str, str]:
    original_name = Path(file.filename or "").name
    extension = Path(original_name).suffix.lower()

    if not original_name or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, PNG and JPEG documents are supported.",
        )

    stored_name = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / stored_name
    total_bytes = 0

    with file_path.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            total_bytes += len(chunk)

            if total_bytes > MAX_UPLOAD_BYTES:
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail="Each document must be 10 MB or smaller.",
                )

            buffer.write(chunk)

    return file_path, stored_name, original_name


# ---------------------------------
# Home
# ---------------------------------

@app.get("/")
def home():
    return {
        "message": "AI Document Verification Agent is running"
    }


# ---------------------------------
# Upload single document
# ---------------------------------

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    file_path, stored_name, original_name = await save_upload(file)

    return {
        "filename": stored_name,
        "original_filename": original_name,
        "content_type": file.content_type,
        "message": "Document uploaded and saved successfully",
        "path": str(file_path),
    }


# ---------------------------------
# Extract OCR text
# ---------------------------------

@app.post("/extract")
async def extract_document_text(filename: str):

    file_path = UPLOAD_DIR / Path(filename).name

    if not os.path.exists(file_path):
        return {
            "error": "File not found"
        }

    extension = os.path.splitext(filename)[1].lower()

    if extension == ".pdf":
        text = extract_text_from_pdf(file_path)

    elif extension in [".png", ".jpg", ".jpeg"]:
        text = extract_text_from_image(file_path)

    else:
        return {
            "error": "Unsupported file type"
        }

    return {
        "filename": filename,
        "extracted_text": text
    }


# ---------------------------------
# Extract KYC
# ---------------------------------

@app.post("/extract-kyc")
async def extract_kyc(filename: str):

    file_path = UPLOAD_DIR / Path(filename).name

    if not os.path.exists(file_path):
        return {
            "error": "File not found"
        }

    extension = os.path.splitext(filename)[1].lower()

    if extension == ".pdf":
        text = extract_text_from_pdf(file_path)

    elif extension in [".png", ".jpg", ".jpeg"]:
        text = extract_text_from_image(file_path)

    else:
        return {
            "error": "Unsupported file type"
        }

    kyc_data = extract_kyc_data(text)

    return {
        "filename": filename,
        "kyc_data": kyc_data
    }


# ---------------------------------
# Process document
# ---------------------------------

@app.post("/process-document")
async def process_uploaded_document(filename: str):

    file_path = UPLOAD_DIR / Path(filename).name

    if not os.path.exists(file_path):
        return {
            "error": "File not found"
        }

    result = process_document(file_path)

    return {
        "filename": filename,
        "result": result
    }


# ---------------------------------
# VALIDATE DOCUMENTS
# ---------------------------------

@app.post("/validate-documents")
async def validate_uploaded_documents(
    aadhaar: UploadFile = File(...),
    pan: UploadFile = File(...),
    bank_statement: UploadFile = File(...)
):

    # ---------------------------------
    # Save uploaded files
    # ---------------------------------

    aadhaar_path, _, _ = await save_upload(aadhaar)
    pan_path, _, _ = await save_upload(pan)
    bank_path, _, _ = await save_upload(bank_statement)


    # ---------------------------------
    # Process documents
    # ---------------------------------

    aadhaar_result = process_document(
        aadhaar_path,
        expected_type="aadhaar",
    )

    pan_result = process_document(
        pan_path,
        expected_type="pan",
    )

    bank_result = process_document(
        bank_path,
        expected_type="bank_statement",
    )


    # ---------------------------------
    # Extract structured data
    # ---------------------------------

    aadhaar_data = aadhaar_result["extracted_data"]

    pan_data = pan_result["extracted_data"]

    bank_data = bank_result["extracted_data"]


    # ---------------------------------
    # Validation Engine
    # ---------------------------------

    validation_results = validate_documents(
        aadhaar_data,
        pan_data,
        bank_data,
        integrity_results={
            "Aadhaar": aadhaar_result["integrity"],
            "PAN": pan_result["integrity"],
            "Bank Statement": bank_result["integrity"],
        },
    )


    # ---------------------------------
    # Deterministic Agent Decision
    # ---------------------------------

    agent_decision = make_verification_decision(
        validation_results
    )


    # ---------------------------------
    # LangChain KYC Agent
    # ---------------------------------

    try:
        kyc_agent_result = run_kyc_agent(
            aadhaar_data,
            pan_data,
            bank_data
        )

    except Exception as e:
        print(f"KYC agent unavailable: {e}")

        kyc_agent_result = (
            "AI agent analysis is currently unavailable. "
            "Deterministic validation results are still available."
        )


    # ---------------------------------
    # Gemini Analysis
    # ---------------------------------

    try:
        gemini_analysis = analyze_validation_results(
            validation_results
        )

    except Exception as e:
        print(f"Gemini analysis unavailable: {e}")

        gemini_analysis = (
            "AI analysis is currently unavailable. "
            "Please review the deterministic validation results."
        )


    # ---------------------------------
    # Verification Report
    # ---------------------------------

    verification_report = generate_verification_report(
        validation_results,
        gemini_analysis
    )


    # ---------------------------------
    # Final Response
    # ---------------------------------

    return {
        "documents": {
            "aadhaar": {
                **aadhaar_data,
                "integrity": aadhaar_result["integrity"],
            },
            "pan": {
                **pan_data,
                "integrity": pan_result["integrity"],
            },
            "bank_statement": {
                **bank_data,
                "integrity": bank_result["integrity"],
            },
        },

        "validation_results": validation_results,

        "agent_decision": agent_decision,

        "kyc_agent_result": kyc_agent_result,

        "gemini_analysis": gemini_analysis,

        "verification_report": verification_report
    }


# ---------------------------------
# Test Gemini
# ---------------------------------

@app.post("/test-gemini")
async def test_gemini():

    test_results = {
        "summary": {
            "total_checks": 3,
            "passed": 2,
            "failed": 1
        },

        "checks": [
            {
                "check": "Name Match: Aadhaar vs PAN",
                "status": "FAIL",
                "message": "Name does not match"
            },

            {
                "check": "DOB Match: Aadhaar vs PAN",
                "status": "PASS",
                "message": "Date of birth matches"
            },

            {
                "check": "PAN Format",
                "status": "PASS",
                "message": "PAN has expected length"
            }
        ]
    }

    analysis = analyze_validation_results(test_results)

    return {
        "gemini_analysis": analysis
    }