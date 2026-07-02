"""
pdf_utils.py
Generates Daily/Weekly/Monthly PDF reports summarizing traffic data,
incidents, alerts, and agent decisions for a given date range.
Uses reportlab (pure Python, no external binaries needed - easy to
install on any machine, which matters for a college project demo).
"""
import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf_report(report_type: str, start_date: date, end_date: date,
                         traffic_summary: dict, incidents: list, alerts: list,
                         agent_logs: list, out_dir="reports_output"):
    """Builds a PDF report and returns the file path."""
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{report_type}_report_{start_date}_{end_date}.pdf"
    filepath = os.path.join(out_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Smart City Traffic Management - {report_type.title()} Report", styles["Title"]))
    elements.append(Paragraph(f"Period: {start_date} to {end_date}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * cm))

    # Traffic summary table
    elements.append(Paragraph("Traffic Summary", styles["Heading2"]))
    summary_data = [["Metric", "Value"]] + [[k, str(v)] for k, v in traffic_summary.items()]
    summary_table = Table(summary_data, colWidths=[8 * cm, 8 * cm])
    summary_table.setStyle(_table_style())
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Incidents table
    elements.append(Paragraph(f"Incidents Reported ({len(incidents)})", styles["Heading2"]))
    if incidents:
        inc_data = [["Road", "Type", "Severity", "Reported At"]] + [
            [i.get("road_name", "-"), i.get("incident_type", "-"),
             i.get("severity", "-"), str(i.get("reported_at", "-"))]
            for i in incidents[:30]
        ]
        inc_table = Table(inc_data, colWidths=[4 * cm, 4 * cm, 3 * cm, 5 * cm])
        inc_table.setStyle(_table_style())
        elements.append(inc_table)
    else:
        elements.append(Paragraph("No incidents reported in this period.", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * cm))

    # Alerts
    elements.append(Paragraph(f"Alerts Generated ({len(alerts)})", styles["Heading2"]))
    for a in alerts[:20]:
        elements.append(Paragraph(f"- {a.get('alert_text', '')}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * cm))

    # Agent decisions
    elements.append(Paragraph(f"Agent Decisions ({len(agent_logs)})", styles["Heading2"]))
    if agent_logs:
        log_data = [["Decision", "Reason", "Urgency"]] + [
            [l.get("decision", "-"), l.get("reason", "-"), l.get("urgency", "-")]
            for l in agent_logs[:30]
        ]
        log_table = Table(log_data, colWidths=[6 * cm, 7 * cm, 3 * cm])
        log_table.setStyle(_table_style())
        elements.append(log_table)
    else:
        elements.append(Paragraph("No agent decisions logged in this period.", styles["Normal"]))

    doc.build(elements)
    return filepath


def _table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])
