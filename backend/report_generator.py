import json
import os

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


def generate_report(data, output_path="results/report.pdf"):
    """
    Generate a PDF attribution report.

    Expected data format:
    {
        "wallet": "...",
        "vasp_name": "...",
        "risk_score": 85,
        "confidence": "...",
        "hop_path": ["wallet1", "wallet2", "wallet3"]
    }
    """

    # Make sure the output directory exists
    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    story = []

    # Title
    story.append(
        Paragraph(
            "CryptoAttrib-AI Attribution Report",
            title_style
        )
    )

    story.append(Spacer(1, 20))

    # Basic attribution information
    report_data = [
        ["Field", "Value"],
        ["Wallet Address", data["wallet"]],
        ["VASP", data["vasp_name"]],
        ["Risk Score", str(data["risk_score"])],
        ["Confidence", data["confidence"]],
    ]

    table = Table(
        report_data,
        colWidths=[150, 350]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # Transaction hop path
    story.append(
        Paragraph(
            "Transaction Hop Path",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 10))

    for index, address in enumerate(
        data["hop_path"],
        start=1
    ):
        story.append(
            Paragraph(
                f"{index}. {address}",
                styles["BodyText"]
            )
        )

        story.append(Spacer(1, 5))

    story.append(Spacer(1, 20))

    # Disclaimer
    story.append(
        Paragraph(
            "<b>Note:</b> This report is generated for "
            "demonstration purposes. Attribution results depend "
            "on the underlying blockchain analysis.",
            styles["BodyText"]
        )
    )

    doc.build(story)


def load_demo_data(
    path="demo-data/ethereum_demo.json"
):
    """
    Load Ethereum demo addresses from JSON.
    """

    with open(path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


if __name__ == "__main__":

    # Load Ethereum demo data
    demo_addresses = load_demo_data()

    # Use the first demo Ethereum address
    wallet = demo_addresses[0]["address"]

    sample_data = {
        "wallet": wallet,
        "vasp_name": "Example VASP",
        "risk_score": 85,
        "confidence": "High",
        "hop_path": [
            wallet,
            "0x8ba1f109551bD432803012645Ac136ddd64DBA72",
            "0x3f5CE5FBFe3E9afB48dF1E0eE7D2c9A4D4F5B6C7"
        ]
    }

    generate_report(sample_data)

    print(
        "Report generated successfully: "
        "results/report.pdf"
    )