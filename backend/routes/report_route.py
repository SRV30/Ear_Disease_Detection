from io import BytesIO
import os
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config import UPLOAD_FOLDER
from database.db import history_collection
from extensions import limiter

report_bp = Blueprint("report", __name__)

CLASS_NAMES = [
    "Acute Otitis Media",
    "Cerumen Impaction",
    "Chronic Otitis Media",
    "Myringosclerosis",
    "Normal",
]


def _filename_from_url(url):
    return os.path.basename(url or "")


def _safe_image_path(url):
    filename = _filename_from_url(url)
    if not filename:
        return None
    path = os.path.join(UPLOAD_FOLDER, filename)
    return path if os.path.isfile(path) else None


def _format_confidence(value):
    try:
        return f"{float(value):.4f}%"
    except (TypeError, ValueError):
        return str(value)


@report_bp.route("/report/<history_id>", methods=["GET"])
@jwt_required()
@limiter.limit("20 per minute")
def download_report(history_id):
    user = get_jwt_identity()

    try:
        object_id = ObjectId(history_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Invalid history id"}), 400

    record = history_collection.find_one({
        "_id": object_id,
        "user": user,
    })

    if not record:
        return jsonify({"error": "History item not found"}), 404

    original_path = _safe_image_path(record.get("image_url"))
    heatmap_path = _safe_image_path(record.get("heatmap_url"))

    if not original_path:
        return jsonify({"error": "Original image is unavailable"}), 404

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Ear Disease Detection Report",
        author="Ear Disease Detection System",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=16,
    )
    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )
    small_style = ParagraphStyle(
        "ReportSmall",
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748b"),
    )

    generated_at = object_id.generation_time.astimezone(timezone.utc)
    generated_text = generated_at.strftime("%d %B %Y, %H:%M UTC")

    story = [
        Paragraph("Ear Disease Detection Report", title_style),
        Paragraph("AI-assisted ear image analysis", subtitle_style),
    ]

    summary_data = [
        ["Report ID", str(record["_id"])],
        ["Generated", generated_text],
        ["Prediction", str(record.get("prediction", "N/A"))],
        ["Confidence", _format_confidence(record.get("confidence"))],
        ["Risk", str(record.get("risk", "N/A"))],
    ]

    summary = Table(summary_data, colWidths=[42 * mm, 125 * mm])
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2ff")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#3730a3")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.extend([summary, Spacer(1, 8)])

    story.append(Paragraph("Analyzed Image", heading_style))
    story.append(Image(original_path, width=82 * mm, height=82 * mm))
    story.append(Spacer(1, 4))

    if heatmap_path:
        story.append(Paragraph("Grad-CAM Explanation Heatmap", heading_style))
        story.append(Image(heatmap_path, width=82 * mm, height=82 * mm))

    story.append(Paragraph("Explanation", heading_style))
    story.append(Paragraph(str(record.get("explanation", "N/A")), body_style))

    story.append(Paragraph("Advice", heading_style))
    story.append(Paragraph(str(record.get("advice", "N/A")), body_style))

    if record.get("extra"):
        story.append(Paragraph("Additional Information", heading_style))
        story.append(Paragraph(str(record["extra"]), body_style))

    probabilities = record.get("probabilities", [])
    if len(probabilities) == len(CLASS_NAMES):
        probability_rows = [["Class", "Probability"]]
        for name, value in zip(CLASS_NAMES, probabilities):
            probability_rows.append([name, _format_confidence(float(value) * 100)])

        story.append(Paragraph("Class Probabilities", heading_style))
        probability_table = Table(
            probability_rows,
            colWidths=[115 * mm, 52 * mm],
            repeatRows=1,
        )
        probability_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e7ff")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#312e81")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(probability_table)

    story.append(Spacer(1, 12))
    story.append(KeepTogether([
        Paragraph(
            "<b>Important:</b> This report is generated by an AI-assisted image "
            "analysis system. It is not a clinical diagnosis and should not replace "
            "evaluation by a qualified healthcare professional.",
            small_style,
        ),
        Spacer(1, 5),
        Paragraph(
            "The Grad-CAM heatmap shows image regions that influenced the model's "
            "prediction; it does not represent a confirmed medical lesion location.",
            small_style,
        ),
    ]))

    doc.build(story)
    buffer.seek(0)

    filename = f"ear_disease_report_{history_id}.pdf"
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
