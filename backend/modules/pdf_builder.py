import io
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


def create_bar_chart(groups):
    """Generates a bar chart drawing for a set of audit groups."""
    drawing = Drawing(400, 160)
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 40
    bc.height = 100
    bc.width = 300

    # Extract data: rates and labels
    data = [tuple(g['rate'] for g in groups)]
    labels = [g['group'] for g in groups]

    bc.data = data
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 20

    # Axis styling
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 0
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = labels

    # Bar Color (Blue to match dashboard)
    bc.bars[0].fillColor = colors.HexColor("#3b82f6")

    drawing.add(bc)
    return drawing


def generate_pdf_content(result: dict, org_name: str, threshold: float) -> bytes:
    """
    Constructs the full PDF report.
    'threshold' is passed from the dashboard slider.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()
    story = []

    # Semantic Colors
    DARK = colors.HexColor("#1a1a1a")
    RED = colors.HexColor("#ef4444")
    GREEN = colors.HexColor("#22c55e")
    ORANGE = colors.HexColor("#f59e0b")

    # Typography
    h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=22, textColor=DARK, alignment=0, spaceAfter=12)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=16, spaceBefore=20, textColor=DARK)
    b = ParagraphStyle("b", parent=styles["Normal"], fontSize=10, leading=14)

    # 1. Header
    story.append(Paragraph("⚖ ALGORITHMIC BIAS AUDIT REPORT", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=DARK, spaceAfter=15))

    # 2. Executive Summary (Synced with Dashboard Risk Level)
    risk = result.get("overall_risk", {})
    risk_level = str(risk.get("level", "N/A")).upper()
    risk_score = risk.get("score", 0)

    # Match visual colors to the risk level provided by the auditor
    risk_color = GREEN if "LOW" in risk_level else RED
    if "MODERATE" in risk_level or "MEDIUM" in risk_level:
        risk_color = ORANGE

    meta_data = [
        [Paragraph("<b>Organisation:</b>", b), org_name],
        [Paragraph("<b>Audit Date:</b>", b), datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")],
        [Paragraph("<b>Fairness Threshold:</b>", b), f"{int(float(threshold) * 100)}% (Slider Level)"],
        [Paragraph("<b>Overall Fairness Score:</b>", b), f"{risk_score}%"],
        [Paragraph("<b>Risk Status:</b>", b), Paragraph(f"<font color='{risk_color}'><b>{risk_level}</b></font>", b)],
    ]

    summary_table = Table(meta_data, colWidths=[60 * mm, 110 * mm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)

    # 3. Detailed Audit Results
    story.append(Paragraph("Detailed Disparity Findings", h2))

    for audit in result.get("audits", []):
        disp = audit.get("disparity", {})
        # USE THE AUDITOR'S FLAG (which is based on the slider)
        is_flagged = disp.get("flag")
        status_label = "FLAGGED" if is_flagged else "PASS"
        status_color = RED if is_flagged else GREEN

        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceBefore=10))
        story.append(Paragraph(f"Attribute: {audit['characteristic']}", styles["Heading3"]))

        stats_text = (
            f"<b>Status:</b> <font color='{status_color}'>{status_label}</font> | "
            f"<b>Impact Ratio:</b> {disp.get('disparate_impact_ratio', 0):.3f} | "
            f"<b>Max Gap:</b> {disp.get('max_disparity', 0):.1f}%"
        )
        story.append(Paragraph(stats_text, b))

        # Bar Chart
        story.append(Spacer(1, 5))
        story.append(create_bar_chart(audit.get('groups', [])))
        story.append(Spacer(1, 10))

        # Group Data Table
        group_data = [["Group", "Sample Size", "Success Rate"]]
        for g in audit.get('groups', []):
            group_data.append([g['group'], str(g['count']), f"{g['rate']}%"])

        gt = Table(group_data, colWidths=[60 * mm, 40 * mm, 40 * mm])
        gt.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.2, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ]))
        story.append(gt)
        story.append(Spacer(1, 15))

    # 4. Mitigations
    if result.get("mitigations"):
        story.append(Paragraph("Recommended Mitigations", h2))
        for mit in result["mitigations"]:
            story.append(Paragraph(f"<b>{mit['title']}</b> ({mit.get('priority', 'medium').upper()})", b))
            story.append(Paragraph(mit.get('description', ''), b))
            story.append(Spacer(1, 5))

    doc.build(story)
    return buf.getvalue()