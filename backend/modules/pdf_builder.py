import io
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


def create_bar_chart(groups):
    drawing = Drawing(400, 160)
    bc = VerticalBarChart()
    bc.x, bc.y, bc.height, bc.width = 50, 40, 100, 300
    bc.data = [tuple(g['rate'] for g in groups)]
    bc.valueAxis.valueMin, bc.valueAxis.valueMax = 0, 100
    bc.categoryAxis.categoryNames = [g['group'] for g in groups]
    bc.bars[0].fillColor = colors.HexColor("#3b82f6")
    drawing.add(bc)
    return drawing


def generate_pdf_content(result: dict, org_name: str, threshold: float) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, margin=20 * mm)
    styles = getSampleStyleSheet()
    story = []

    RED, ORANGE, GREEN = colors.HexColor("#ef4444"), colors.HexColor("#f59e0b"), colors.HexColor("#22c55e")

    risk = result.get("overall_risk", {})
    risk_level = str(risk.get("level", "N/A")).upper()
    risk_color = GREEN if "LOW" in risk_level else (ORANGE if "MODERATE" in risk_level else RED)

    story.append(Paragraph("⚖ ALGORITHMIC BIAS AUDIT REPORT", styles["Title"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=10))

    meta_data = [
        ["Organisation:", org_name],
        ["Fairness Threshold:", f"{int(float(threshold) * 100)}%"],
        ["Risk Status:", Paragraph(f"<font color='{risk_color}'><b>{risk_level}</b></font>", styles["Normal"])]
    ]
    t = Table(meta_data, colWidths=[60 * mm, 110 * mm])
    t.setStyle(
        TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke)]))
    story.append(t)

    for audit in result.get("audits", []):
        is_flagged = audit['disparity']['flag']
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"<b>Attribute: {audit['characteristic']}</b>", styles["Heading3"]))
        story.append(Paragraph(
            f"Status: <font color='{RED if is_flagged else GREEN}'>{'FLAGGED' if is_flagged else 'PASS'}</font>",
            styles["Normal"]))
        story.append(create_bar_chart(audit['groups']))

    doc.build(story)
    return buf.getvalue()