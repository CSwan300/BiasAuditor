import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


def create_bar_chart(groups):
    if not groups:
        return Spacer(1, 10)

    drawing = Drawing(400, 160)
    bc = VerticalBarChart()
    bc.x, bc.y, bc.height, bc.width = 50, 40, 100, 300

    rates = [float(g.get('rate', 0)) for g in groups]
    bc.data = [tuple(rates)]

    bc.valueAxis.valueMin, bc.valueAxis.valueMax = 0, 100
    bc.categoryAxis.categoryNames = [str(g.get('group', 'Unknown')) for g in groups]
    bc.bars[0].fillColor = colors.HexColor("#3b82f6")
    drawing.add(bc)
    return drawing


def generate_pdf_content(result: dict, org_name: str, threshold: float) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, margin=20 * mm)
    styles = getSampleStyleSheet()
    story = []

    RED = colors.HexColor("#ef4444")
    ORANGE = colors.HexColor("#f59e0b")
    GREEN = colors.HexColor("#22c55e")

    risk = result.get("overall_risk", {})
    risk_level = str(risk.get("level", "UNKNOWN")).upper()

    risk_color = GREEN
    if "HIGH" in risk_level or "CRITICAL" in risk_level:
        risk_color = RED
    elif "MODERATE" in risk_level:
        risk_color = ORANGE

    story.append(Paragraph("⚖ ALGORITHMIC BIAS AUDIT REPORT", styles["Title"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=10))

    try:
        display_threshold = f"{int(float(threshold) * 100)}%"
    except Exception:  # Fixed E722
        display_threshold = "80%"

    meta_data = [
        ["Organisation:", str(org_name)],
        ["Fairness Threshold:", display_threshold],
        ["Risk Status:", Paragraph(f"<font color='{risk_color}'><b>{risk_level}</b></font>", styles["Normal"])]
    ]
    t = Table(meta_data, colWidths=[60 * mm, 110 * mm])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('PADDING', (0, 0), (-1, -1), 6)
    ]))
    story.append(t)

    audits = result.get("audits", [])
    if not audits:
        story.append(Spacer(1, 20))
        story.append(Paragraph("No audit data available for this report.", styles["Normal"]))

    for audit in audits:
        disparity = audit.get('disparity', {})
        is_flagged = disparity.get('flag', False)
        char_name = audit.get('characteristic', 'Unknown Attribute')

        story.append(Spacer(1, 15))
        story.append(Paragraph(f"<b>Attribute: {char_name}</b>", styles["Heading3"]))

        status_text = "FLAGGED" if is_flagged else "PASS"
        status_color = RED if is_flagged else GREEN
        story.append(Paragraph(
            f"Status: <font color='{status_color}'><b>{status_text}</b></font>",
            styles["Normal"]))

        try:
            chart = create_bar_chart(audit.get('groups', []))
            story.append(chart)
        except Exception as e:
            story.append(Paragraph(f"[Chart Generation Error: {str(e)}]", styles["Italic"]))

    doc.build(story)
    return buf.getvalue()