"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Core Asset Engine: Standard Industrial PDF Sign Sheet Compiler (Vector SVG Native)
"""

import os
import logging
from reportlab.lib.pagesizes import letter, mm
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from config.database import get_db_cursor

logger = logging.getLogger("McjRoadSigns.PDFCompiler")

STORAGE_BASE_PATH = os.getenv("STORAGE_BASE_PATH", "./storage")

def compile_print_pdf(qr_metadata: dict) -> str:
    """
    Takes the generated vector QR dictionary mapping from qr_generator.py,
    reads physical master blueprint dimensions from PostgreSQL, and
    compiles a permanent, high-resolution printable PDF worksheet.
    """
    sign_uid = qr_metadata["sign_uid"]
    qr_svg_path = qr_metadata["qr_svg_absolute_path"]
    pdf_destination_path = qr_metadata["pdf_absolute_path"]

    # 1. Fetch physical layout boundaries from the database
    dimensions_query = """
        SELECT m.size_width_mm, m.size_height_mm, m.sign_shape, m.irc_sign_code
        FROM sign_instances i
        JOIN sign_masters m ON i.master_id = m.master_id
        WHERE i.sign_uid = %s;
    """
    
    width_mm = 600  # Engineering defaults if mapping check falls through
    height_mm = 600
    shape_name = "Circle"
    irc_code = "IRC-UNKNOWN"

    try:
        with get_db_cursor() as cursor:
            cursor.execute(dimensions_query, (sign_uid,))
            record = cursor.fetchone()
            if record:
                width_mm, height_mm, shape_name, irc_code = record

        # 2. Configure ReportLab canvas to match the physical engineering footprint
        canvas_width = width_mm * mm
        canvas_height = height_mm * mm
        
        pdf_canvas = canvas.Canvas(pdf_destination_path, pagesize=(canvas_width, canvas_height))
        
        # 3. Draw Layout Alignment Boundaries (Helps factory machine cutting trims)
        pdf_canvas.setStrokeColorRGB(0.7, 0.7, 0.7) # Muted gray trim border lines
        pdf_canvas.setLineWidth(1)
        pdf_canvas.rect(5, 5, canvas_width - 10, canvas_height - 10)
        
        # 4. Embed Municipal Typography & Design Meta Headers
        pdf_canvas.setFillColorRGB(0.06, 0.09, 0.16) # Deep dark state slate profile color
        pdf_canvas.setFont("Helvetica-Bold", int(canvas_height * 0.04))
        pdf_canvas.drawCentredString(canvas_width / 2.0, canvas_height - (canvas_height * 0.08), "MUNICIPAL CORPORATION JALANDHAR")
        
        pdf_canvas.setFont("Helvetica", int(canvas_height * 0.03))
        meta_label = f"Asset ID: {sign_uid}   |   Code: {irc_code}   |   Shape: {shape_name} ({width_mm}x{height_mm}mm)"
        pdf_canvas.drawCentredString(canvas_width / 2.0, canvas_height - (canvas_height * 0.13), meta_label)

        # 5. Native Vector SVG Parsing and Canvas Rendering Flow
        # Converts the raw vector file coordinates layout cleanly into a ReportLab drawing block
        drawing = svg2rlg(qr_svg_path)
        
        # Calculate bounding boxes to keep the code perfectly centered
        qr_display_size = min(canvas_width, canvas_height) * 0.55
        
        # Scale the vector graphic down dynamically to match our target layout print dimension properties
        factor = qr_display_size / drawing.width
        drawing.scale(factor, factor)
        
        qr_x_position = (canvas_width - qr_display_size) / 2.0
        qr_y_position = (canvas_height - qr_display_size) / 2.1
        
        # Draw the unalterable vector graph coordinates straight onto the canvas layers
        renderPDF.draw(drawing, pdf_canvas, qr_x_position, qr_y_position)
        
        # 6. Corporate Branding Footer Insertion Line
        pdf_canvas.setFont("Helvetica-Oblique", int(canvas_height * 0.025))
        pdf_canvas.setFillColorRGB(0.4, 0.4, 0.4)
        pdf_canvas.drawCentredString(canvas_width / 2.0, canvas_height * 0.06, "System Extension Add-On. Secure City Scale QR Infrastructure Asset.")
        
        # Save and close the file lock handle
        pdf_canvas.showPage()
        pdf_canvas.save()
        
        logger.info(f"High-resolution printable sign board PDF generated successfully: {pdf_destination_path}")
        return pdf_destination_path

    except Exception as error:
        logger.error(f"Failed to compile printable PDF sheet layout for reference {sign_uid}: {error}")
        raise error
