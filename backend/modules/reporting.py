# backend/modules/reporting.py
import io
import traceback
from datetime import datetime
from fastapi.responses import StreamingResponse
from .pdf_builder import generate_pdf_content


def build_pdf_response(result: dict, org_name: str, threshold: float = 0.80):
    try:
        pdf_bytes = generate_pdf_content(result, org_name, threshold)

        # Verification check
        if not pdf_bytes:
            raise ValueError("Generated PDF bytes are empty")

        filename = f"bias_audit_{datetime.now().strftime('%Y%m%d')}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            },
        )
    except Exception as e:
        # This will print the actual error to your PyCharm console
        print("❌ PDF BUILDER FAILED:")
        print(traceback.format_exc())
        # Return a simple text error so the frontend knows what happened
        raise e