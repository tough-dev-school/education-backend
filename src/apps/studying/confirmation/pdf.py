from pathlib import Path

from django.conf import settings
from django.utils import timezone
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from apps.studying.models import Study

FONT_SIZE = 14


def get_pdf(study: Study) -> bytes:
    date = timezone.now()
    title = "Справка"
    content = f"Выдана {study.student} в том, что он прослушал курс «{study.course.product_name}»."
    document_number = f"№ {study.order.id} от {date.day:02d}.{date.month:02d}.{date.year}"

    pdf = FPDF()
    pdf.add_page()

    pdf.add_font(
        "PT Serif",
        fname=str(
            Path(settings.BASE_DIR) / "paperwork/PT_Serif-Web-Regular.ttf",
        ),
    )
    pdf.add_font(
        "PT Serif",
        style="B",
        fname=str(
            Path(settings.BASE_DIR) / "paperwork/PT_Serif-Web-Bold.ttf",
        ),
    )

    pdf.set_font("PT Serif", size=FONT_SIZE)

    # Add logo (full-width at top-left corner)
    pdf.image(str(Path(settings.BASE_DIR / "paperwork/logo.jpg")), x=0, y=0, w=210)  # Full-width A4 (210mm), top-left corner

    # Add document number text (left-aligned, below logo)
    pdf.ln(60)  # Move below full-width logo
    pdf.cell(0, 10, document_number, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")

    # Add title (centered, below document number, bold)
    pdf.ln(5)  # Small spacing
    pdf.set_font("PT Serif", style="B", size=FONT_SIZE)  # Set bold font for title
    pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("PT Serif", size=FONT_SIZE)  # Reset to regular font for content

    # Add content (justified text)
    pdf.ln(10)
    pdf.set_xy(10, pdf.get_y())  # Set left margin
    pdf.multi_cell(0, 8, content, align="J")

    if settings.SIGNATURE_PATH != "/dev/null":
        signature_width = 30  # 30mm wide
        signature_x = 190 - signature_width - 30  # A4 width (210mm) - fields signature width - margin
        signature_y = 130
        pdf.image(str(settings.SIGNATURE_PATH), x=signature_x, y=signature_y, w=signature_width)

        # Add signature text below image
        signature_text = f"____________ {settings.COMPANY_NAME}"
        text_x = signature_x + 10
        text_y = signature_y + 15  # Below signature (assuming ~20mm signature height)
        pdf.set_xy(text_x, text_y)
        pdf.cell(signature_width, 5, signature_text, align="C")

    return bytes(pdf.output())
