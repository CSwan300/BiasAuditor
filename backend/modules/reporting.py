import io
from datetime import datetime, timezone
from fastapi.responses import StreamingResponse
from .pdf_builder import generate_pdf_content

def build_pdf_response(result: dict, org_name: str, threshold: float = 0.80):
    """
    Generates PDF and returns a StreamingResponse.
    Added a default for threshold to prevent 500 errors if argument is missing.
    """
    # Ensure threshold is passed to the actual builder
    pdf_bytes = generate_pdf_content(result, org_name, threshold)
    filename = f"bias_audit_report_{datetime.now().strftime('%Y%m%d')}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        },
    )

def build_json_report(result: dict, org_name: str, threshold: float):
    return {
        "report_metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "organisation": org_name,
            "fairness_threshold": threshold,
            "legal_disclaimer": "Internal monitoring only. Not legal advice."
        },
        "audit_results": result,
    }