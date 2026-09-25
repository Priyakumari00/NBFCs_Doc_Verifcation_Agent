def make_verification_decision(validation_results):
    """
    Decide whether the submitted documents can be automatically
    verified based on the deterministic validation results.
    """

    summary = validation_results["summary"]
    risk_flags = validation_results["risk_flags"]
    completeness = validation_results["document_completeness"]

    # 1. Missing documents
    if completeness["status"] == "INCOMPLETE":
        return {
            "verification_status": "NEEDS_REVIEW",
            "reason": "One or more required documents are missing.",
            "risk_flags": risk_flags,
            "automated_checks": {
                "total": summary["total_checks"],
                "passed": summary["passed"],
                "failed": summary["failed"]
            }
        }

    # 2. Any validation failure
    if summary["failed"] > 0:
        return {
            "verification_status": "NEEDS_REVIEW",
            "reason": "One or more document validation checks failed.",
            "risk_flags": risk_flags,
            "automated_checks": {
                "total": summary["total_checks"],
                "passed": summary["passed"],
                "failed": summary["failed"]
            }
        }

    # 3. Any risk flag
    if len(risk_flags) > 0:
        return {
            "verification_status": "NEEDS_REVIEW",
            "reason": "Risk flags were identified during document validation.",
            "risk_flags": risk_flags,
            "automated_checks": {
                "total": summary["total_checks"],
                "passed": summary["passed"],
                "failed": summary["failed"]
            }
        }

    # 4. Everything passed
    return {
        "verification_status": "VERIFIED",
        "reason": (
            "All required documents are present and all configured "
            "automated validation checks passed."
        ),
        "risk_flags": [],
        "automated_checks": {
            "total": summary["total_checks"],
            "passed": summary["passed"],
            "failed": summary["failed"]
        }
    }