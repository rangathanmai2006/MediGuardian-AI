from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

import os


def create_pdf(analysis):

    output_path = "AI_Medical_Report.pdf"

    doc = SimpleDocTemplate(output_path)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("<b>MediGuardian AI Report</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"<b>Report Type:</b> {analysis.get('report_type','N/A')}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Health Score:</b> {analysis.get('health_score','N/A')}/100",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Priority:</b> {analysis.get('priority','N/A')}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Doctor Visit:</b> {analysis.get('doctor_visit','N/A')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>Summary</b>", styles["Heading2"]))

    elements.append(
        Paragraph(
            analysis.get("summary",""),
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>Key Findings</b>", styles["Heading2"]))

    for item in analysis.get("key_findings", []):
        elements.append(
            Paragraph("• " + item, styles["Normal"])
        )

    elements.append(Spacer(1, 20))

    for card in analysis.get("cards", []):

        elements.append(
            Paragraph(
                f"<b>{card['title']}</b>",
                styles["Heading2"]
            )
        )

        elements.append(
            Paragraph(
                card["description"],
                styles["Normal"]
            )
        )

        elements.append(Spacer(1, 10))

    doc.build(elements)

    return os.path.abspath(output_path)