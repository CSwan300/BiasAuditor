import io
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)


def generate_pdf_content(result: dict, org_name: str, threshold: float) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=25 * mm, bottomMargin=25 * mm)
    styles = getSampleStyleSheet()
    story = []

    # UI Colors matching your dashboard
    DARK = colors.HexColor("#0d0d0d")
    RED = colors.HexColor("#ff4444")
    GREEN = colors.HexColor("#00cc66")
    AMBER = colors.HexColor("#ffaa00")

    h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=22, textColor=DARK, alignment=0)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=14, spaceBefore=15, textColor=DARK)
    b = ParagraphStyle("b", parent=styles["Normal"], fontSize=10, leading=14)

    # 1. Header
    story.append(Paragraph("⚖ ALGORITHMIC BIAS AUDIT REPORT", h1))
    story.append(HRFlowable(width="100%", thickness=2, color=DARK, spaceAfter=10))

    # 2. Extract Overall Risk Data
    risk_obj = result.get("overall_risk", {})
    risk_level = risk_obj.get("level", "Unknown")
    risk_score = risk_obj.get("score", 0)
    flagged_list = ", ".join(risk_obj.get("flagged_characteristics", [])) or "None"

    # 3. Summary Table
    meta_data = [
        ["Organisation:", org_name],
        ["Generated:", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")],
        ["Risk Level:", f"{risk_level.upper()} ({risk_score}%)"],
        ["Flagged:", flagged_list],
    ]

    t = Table(meta_data, colWidths=[40 * mm, 130 * mm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # 4. Detailed Findings (Looping through 'audits')
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Paragraph("Detailed Characteristic Analysis", h2))
    story.append(Spacer(1, 5))

    # Use .get("audits") to match your auditor.py output
    for audit in result.get("audits", []):
        char_name = audit.get("characteristic", "Unknown")
        disparity = audit.get("disparity", {})
        is_flagged = disparity.get("flag", False)

        status_text = "FLAGGED" if is_flagged else "PASS"
        status_color = RED if is_flagged else GREEN

        # Characteristic Header
        story.append(Paragraph(f"<b>{char_name}</b>", b))

        # Details
        ratio = disparity.get("disparate_impact_ratio", 0)
        gap = disparity.get("max_disparity", 0)

        detail_text = (
            f"Status: <font color='{status_color}'>{status_text}</font> | "
            f"Impact Ratio: {ratio:.3f} | Max Gap: {gap * 100:.1%}"
        )
        story.append(Paragraph(detail_text, b))
        story.append(Spacer(1, 5))

    doc.build(story)
    return buf.getvalue()