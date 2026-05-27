import io
from datetime import datetime
from fastapi.responses import StreamingResponse
from backend.modules.Build_pdf.pdf_builder import generate_pdf_content

def build_pdf_response(result: dict, org_name: str, threshold: float = 0.80):
    try:
        pdf_bytes = generate_pdf_content(result, org_name, threshold)

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
        raise e