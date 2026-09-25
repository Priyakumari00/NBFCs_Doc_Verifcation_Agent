def generate_verification_report(
    validation_results,
    gemini_analysis
):
    summary = validation_results["summary"]
    completeness = validation_results["document_completeness"]

    report = {
        "verification_report": {
            "document_status": completeness["status"],

            "document_summary": {
                "required": completeness["required_documents"],
                "present": completeness["present_documents"],
                "missing": completeness["missing_documents"]
            },

            "checks": {
                "total": summary["total_checks"],
                "passed": summary["passed"],
                "failed": summary["failed"]
            },

            "risk_assessment": {
                "priority": validation_results["review_priority"],
                "flags": validation_results["risk_flags"]
            },

            "human_review_required": True,

            "ai_summary": gemini_analysis,

            "disclaimer": (
                "This automated analysis assists human review. "
                "It does not establish document authenticity and "
                "does not make a final KYC or lending decision."
            )
        }
    }

    return {
    "document_status": completeness["status"],

    "document_summary": {
        "required": completeness["required_documents"],
        "present": completeness["present_documents"],
        "missing": completeness["missing_documents"]
    },

    "checks": {
        "total": summary["total_checks"],
        "passed": summary["passed"],
        "failed": summary["failed"]
    },

    "risk_assessment": {
        "priority": validation_results["review_priority"],
        "flags": validation_results["risk_flags"]
    },

    "human_review_required": True,

    "ai_summary": gemini_analysis,

    "disclaimer": (
        "This automated analysis assists human review. "
        "It does not establish document authenticity and "
        "does not make a final KYC or lending decision."
    )
}