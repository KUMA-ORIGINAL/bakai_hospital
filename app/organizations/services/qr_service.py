from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode


def create_qr_code_in_memory(url, size_px=250):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=0,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')

    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    return qr_buffer


def create_overlay_pdf(qr_image_buffer, text_department, text_room):
    packet = BytesIO()
    page_width, page_height = landscape(A4)
    can = canvas.Canvas(packet, pagesize=landscape(A4))

    pdfmetrics.registerFont(TTFont('SF Pro Text Medium', 'static/fonts/SFProText-Medium.ttf'))
    pdfmetrics.registerFont(TTFont('SF Pro Text Heavy', 'static/fonts/SFProText-Heavy.ttf'))

    qr_image = ImageReader(qr_image_buffer)
    qr_width = 220
    qr_height = 220

    section_width = page_width / 2
    x1 = (section_width - qr_width) / 2
    x2 = page_width - section_width + (section_width - qr_width) / 2

    y_center = (page_height / 2) - 10
    y1 = y_center - (qr_height / 2) + 53
    y2 = y1

    can.drawImage(qr_image, x1, y1, width=qr_width, height=qr_height)
    can.drawImage(qr_image, x2, y2, width=qr_width, height=qr_height)

    can.setFont('SF Pro Text Medium', 12)
    can.setFillColor(HexColor("#FFFFFF"))

    dept_width1 = pdfmetrics.stringWidth(text_department, 'SF Pro Text Medium', 12)
    can.drawString(x1 + (qr_width - dept_width1) / 2, y1 + 280, text_department)

    can.setFont('SF Pro Text Heavy', 24)
    room_width1 = pdfmetrics.stringWidth(text_room, 'SF Pro Text Heavy', 24)
    can.drawString(x1 + (qr_width - room_width1) / 2, y1 + 250, text_room)

    can.setFont('SF Pro Text Medium', 12)
    dept_width2 = pdfmetrics.stringWidth(text_department, 'SF Pro Text Medium', 12)
    can.drawString(x2 + (qr_width - dept_width2) / 2, y2 + 280, text_department)

    can.setFont('SF Pro Text Heavy', 24)
    room_width2 = pdfmetrics.stringWidth(text_room, 'SF Pro Text Heavy', 24)
    can.drawString(x2 + (qr_width - room_width2) / 2, y2 + 250, text_room)

    can.save()
    packet.seek(0)
    return PdfReader(packet)


def process_pdf(qr_url, text_department, text_room):
    qr_image_buffer = create_qr_code_in_memory(qr_url)
    overlay_pdf = create_overlay_pdf(qr_image_buffer, text_department, text_room)

    input_pdf = 'static/pdfs/input.pdf'

    if isinstance(input_pdf, str):
        with open(input_pdf, "rb") as pdf_file:
            pdf_data = pdf_file.read()
        reader = PdfReader(BytesIO(pdf_data))
    else:
        reader = PdfReader(input_pdf)

    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output

