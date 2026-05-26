import csv
import io
import sys
from types import ModuleType

# Graceful Pillow (PIL) mocking block to bypass reportlab's hard import requirement on Pillow
try:
    import PIL
    import PIL.Image
except ImportError:
    pil_mock = ModuleType("PIL")
    image_mock = ModuleType("PIL.Image")
    pil_mock.Image = image_mock
    image_mock.Image = object
    sys.modules["PIL"] = pil_mock
    sys.modules["PIL.Image"] = image_mock

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import List, Dict, Any

def generate_csv_report(event_title: str, attendees: List[Dict[str, Any]]) -> str:
    """
    Generates a beautifully organized CSV string containing event attendance.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Student Name", 
        "Student Number", 
        "Email", 
        "Department", 
        "Course", 
        "Time In", 
        "Registration Date"
    ])
    
    for a in attendees:
        writer.writerow([
            a.get("name"),
            a.get("student_number") or "N/A",
            a.get("email"),
            a.get("department") or "N/A",
            a.get("course") or "N/A",
            a.get("scanned_at") or "N/A",
            a.get("registered_at") or "N/A"
        ])
        
    return output.getvalue()

def generate_pdf_report(event_title: str, event_date: str, attendees: List[Dict[str, Any]]) -> bytes:
    """
    Generates a highly-polished, enterprise-grade PDF report of attendance
    using ReportLab with clean styling and professional palettes.
    """
    buffer = io.BytesIO()
    
    # 8.5 x 11 inches is 612 x 792 points. Margins are 40pt each side, usable width = 532pt.
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Create gorgeous custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#1A365D'),  # Sleek deep navy
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#4A5568'),  # Elegant warm grey
        spaceAfter=15
    )
    
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#2D3748')
    )
    
    header_cell_style = ParagraphStyle(
        'TableHeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white,
        leading=11
    )

    summary_style = ParagraphStyle(
        'SummaryText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=15
    )

    # 1. Header Section
    story.append(Paragraph("Event Attendance Report", title_style))
    story.append(Paragraph(f"<b>Event:</b> {event_title} &nbsp;|&nbsp; <b>Date:</b> {event_date}", subtitle_style))
    story.append(Spacer(1, 10))

    # 2. Table Section
    # Headers
    table_data = [[
        Paragraph("Name", header_cell_style),
        Paragraph("Student No.", header_cell_style),
        Paragraph("Department", header_cell_style),
        Paragraph("Course", header_cell_style),
        Paragraph("Time In", header_cell_style)
    ]]

    # Row items
    for a in attendees:
        table_data.append([
            Paragraph(a.get("name"), cell_style),
            Paragraph(a.get("student_number") or "N/A", cell_style),
            Paragraph(a.get("department") or "N/A", cell_style),
            Paragraph(a.get("course") or "N/A", cell_style),
            Paragraph(a.get("scanned_at") or "N/A", cell_style)
        ])

    # Margins and dimensions: 150 + 80 + 110 + 92 + 100 = 532pt
    col_widths = [150, 80, 110, 92, 100]
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Beautiful table styling
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),  # Dark Navy Header
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),  # Alternating white/grey
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),  # Soft border dividers
    ]))
    
    story.append(table)
    
    # 3. Summary section
    total_attendees = len(attendees)
    story.append(Paragraph(f"Total Scanned Attendance: {total_attendees} students", summary_style))
    
    # Build document
    doc.build(story)
    
    return buffer.getvalue()
