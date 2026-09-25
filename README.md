# NBFC Document Verification Agent

An AI-assisted document verification workspace for NBFC compliance teams. The system reviews Aadhaar, PAN, and bank statement uploads for basic readability, document integrity, field validity, and cross-document consistency, then gives a human reviewer an evidence-backed recommendation.

> This project supports human review. It does not prove legal authenticity, replace issuer verification, approve or reject loans, or make a final KYC decision.

## What It Does

- Accepts Aadhaar, PAN, and bank statement files in PDF, PNG, and JPEG formats.
- Extracts text with OCR using Tesseract.
- Identifies the document type and extracts common KYC fields.
- Checks PAN, IFSC, and bank account number formats.
- Compares names and dates of birth across submitted documents.
- Detects review indicators such as:
  - Very low OCR readability
  - Poor OCR text quality
  - Low image resolution
  - Malformed or unreadable files
  - Encrypted PDFs
  - Unexpected document types
  - Missing or inconsistent fields
- Produces a deterministic `VERIFIED` or `NEEDS_REVIEW` recommendation.
- Uses Gemini/LangChain to provide additional analysis and reviewer-friendly explanations when configured.
- Shows the recommendation, extracted fields, checks, and risk indicators in the React reviewer interface.

## Architecture

```text
React reviewer UI
        |
        | multipart upload: Aadhaar + PAN + bank statement
        v
FastAPI /validate-documents
        |
        +--> OCR and document classification
        +--> Structured field extraction
        +--> File integrity and readability checks
        +--> Cross-document validation
        +--> Deterministic verification decision
        +--> Optional Gemini/LangChain explanation
        v
Evidence-backed reviewer result
```

### Important decision boundary

The deterministic validation layer owns the final recommendation. The language model summarizes evidence and performs agent-tool checks, but it is not allowed to make lending decisions or override failed deterministic checks.

## Project Structure

```text
backend/
  main.py                 FastAPI application and API routes
  document_processor.py   OCR, classification, and field extraction orchestration
  document_integrity.py   File, image/PDF, OCR, and fingerprint checks
  validation_engine.py    Deterministic KYC and consistency validation
  agent_decision.py       VERIFIED / NEEDS_REVIEW decision logic
  kyc_agent.py            Optional LangChain Gemini agent
  gemini_service.py       Optional Gemini reviewer summary
  verification_report.py  Human-review report construction
  ocr_service.py          Tesseract and PyMuPDF OCR integration
  *_extractor.py          Structured field extraction helpers

frontend/
  src/App.jsx             Reviewer dashboard and upload workflow
  src/components/ui/      UI components
```

## Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer
- Tesseract OCR
- A Gemini API key for the optional model-backed analysis

The current OCR service uses this Windows path by default:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Update `backend/ocr_service.py` if Tesseract is installed elsewhere.

## Backend Setup

From the repository root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install fastapi uvicorn python-multipart python-dotenv pytesseract pymupdf Pillow google-genai langchain langchain-core langchain-google-genai
```

Create a `.env` file in the repository root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Start the API:

```powershell
uvicorn backend.main:app --reload --port 8000
```

The API will be available at:

- `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## Frontend Setup

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

The frontend expects the backend at `http://127.0.0.1:8000`.

## Main API Routes

### `POST /validate-documents`

Accepts three multipart files:

- `aadhaar`
- `pan`
- `bank_statement`

Returns:

- Extracted document data
- Integrity checks and SHA-256 fingerprints
- Validation checks and risk flags
- Deterministic agent decision
- Optional KYC agent analysis
- Optional Gemini summary
- Human-review report

Example with PowerShell:

```powershell
$form = @{
  aadhaar = Get-Item .\samples\aadhaar.pdf
  pan = Get-Item .\samples\pan.pdf
  bank_statement = Get-Item .\samples\bank_statement.pdf
}
Invoke-RestMethod -Uri http://127.0.0.1:8000/validate-documents -Method Post -Form $form
```

### Other routes

- `GET /` - Health message
- `POST /upload` - Store one supported document securely
- `POST /extract?filename=...` - Return OCR text for a stored upload
- `POST /extract-kyc?filename=...` - Return extracted KYC fields
- `POST /process-document?filename=...` - Run classification and processing
- `POST /test-gemini` - Test the Gemini summary integration

## Verification Behavior

The result is `VERIFIED` only when all required documents are present and the configured checks pass without risk flags.

The result is `NEEDS_REVIEW` when any of the following occurs:

- A required document is missing.
- OCR cannot reliably read the document.
- The file is malformed, encrypted, or structurally suspicious.
- The submitted document type does not match the expected type.
- A name or date of birth does not match across documents.
- A PAN, IFSC, or account number format is invalid or missing.
- Any other configured risk flag is raised.

A `VERIFIED` result means the configured automated checks passed. It does not establish that a document was issued by the claimed authority or that it is free from sophisticated manipulation.

## Security Notes

- Uploads are limited to PDF, PNG, and JPEG files.
- Backend uploads are limited to 10 MB per file.
- Stored filenames are generated by the server rather than trusted from client input.
- `.env`, virtual environments, dependencies, generated builds, and uploaded documents are excluded from Git.
- Do not commit API keys, real customer documents, or personally identifiable information.
- Use HTTPS, authentication, authorization, audit logging, retention policies, and encrypted storage before deploying with production customer data.

## Validation and Build Checks

Backend syntax check:

```powershell
python -m compileall backend
```

Frontend production build:

```powershell
cd frontend
npm run build
```

## Current Limitations

- OCR and regex extraction are heuristic and require representative document samples and testing.
- No direct Aadhaar, PAN, or bank issuer API verification is implemented.
- No forensic image analysis, digital-signature validation, or trusted-source comparison is implemented.
- The current UI uses a fixed backend URL and is intended for local development.
- The optional model integrations require a valid Gemini API key and compatible model access.
- Human review remains mandatory for risk flags and should be mandatory before any regulated decision.

## Roadmap

- Add authenticated reviewer accounts and role-based access.
- Add persistent case records and immutable audit history.
- Add configurable document policies per NBFC product.
- Add issuer or trusted-source verification integrations.
- Add stronger PDF, image, metadata, and digital-signature forensics.
- Add automated tests with redacted synthetic documents.
- Move configuration such as OCR path, API URL, file limits, and model names into environment settings.

## License

No license has been specified yet.
