from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode


def generate_qr_pdf(
    qr_url,
    text_department,
    text_room,
    site_text,
    scan_text_ru,
    pay_text_ru,
    scan_text_kg,
    pay_text_kg,
):
    # === 1. Создание QR-кода ===
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=0,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_image = ImageReader(qr_buffer)

    # === 2. Создание оверлей-PDF с надписями ===
    packet = BytesIO()
    page_width, page_height = landscape(A4)
    can = canvas.Canvas(packet, pagesize=landscape(A4))

    # Регистрируем шрифты
    pdfmetrics.registerFont(TTFont('SF Pro Text Medium', 'static/fonts/SFProText-Medium.ttf'))
    pdfmetrics.registerFont(TTFont('SF Pro Text Heavy', 'static/fonts/SFProText-Heavy.ttf'))

    qr_width = 220
    qr_height = 220

    section_width = page_width / 2
    x1 = (section_width - qr_width) / 2
    x2 = page_width - section_width + (section_width - qr_width) / 2

    y_center = (page_height / 2) - 10
    y1 = y_center - (qr_height / 2) + 53
    y2 = y1

    # QR изображение
    can.drawImage(qr_image, x1, y1, width=qr_width, height=qr_height)
    can.drawImage(qr_image, x2, y2, width=qr_width, height=qr_height)

    can.setFont('SF Pro Text Medium', 12)
    can.setFillColor(Color(1, 1, 1, alpha=0.85))
    dept_width = pdfmetrics.stringWidth(text_department, 'SF Pro Text Medium', 12)
    can.drawString(x1 + (qr_width - dept_width) / 2, y1 + 280, text_department)
    can.drawString(x2 + (qr_width - dept_width) / 2, y2 + 280, text_department)

    can.setFont('SF Pro Text Heavy', 24)
    can.setFillColor(HexColor("#FFFFFF"))
    room_width = pdfmetrics.stringWidth(text_room, 'SF Pro Text Heavy', 24)
    can.drawString(x1 + (qr_width - room_width) / 2, y1 + 250, text_room)
    can.drawString(x2 + (qr_width - room_width) / 2, y2 + 250, text_room)

    # === Нижние надписи ===

    # 1. www.hospital.kg — 18 pt, bold, black
    can.setFont('SF Pro Text Heavy', 18)
    site_width = pdfmetrics.stringWidth(site_text, 'SF Pro Text Heavy', 18)
    can.drawString(x1 + (qr_width - site_width) / 2, y1 - 40, site_text)
    can.drawString(x2 + (qr_width - site_width) / 2, y2 - 40, site_text)

    # 2. Отсканируйте камерой телефон — 12 pt, medium, white with 85% opacity
    can.setFont('SF Pro Text Medium', 12)
    can.setFillColor(Color(1, 1, 1, alpha=0.85))
    scan_width_ru = pdfmetrics.stringWidth(scan_text_ru, 'SF Pro Text Medium', 12)
    scan_width_kg = pdfmetrics.stringWidth(scan_text_kg, 'SF Pro Text Medium', 12)
    can.drawString(x1 + (qr_width - scan_width_ru) / 2, y1 - 60, scan_text_ru)
    can.drawString(x2 + (qr_width - scan_width_kg) / 2, y2 - 60, scan_text_kg)

    # 3. Оплачивайте через — 12 pt, medium, #111827
    can.setFont('SF Pro Text Medium', 12)
    can.setFillColor(HexColor("#111827"))
    pay_width_ru = pdfmetrics.stringWidth(pay_text_ru, 'SF Pro Text Medium', 12)
    pay_width_kg = pdfmetrics.stringWidth(pay_text_kg, 'SF Pro Text Medium', 12)
    can.drawString(x1 + (qr_width - pay_width_ru) / 2, y1 - 170, pay_text_ru)
    can.drawString(x2 + (qr_width - pay_width_kg) / 2, y2 - 170, pay_text_kg)

    # Сохраняем оверлей
    can.save()
    packet.seek(0)
    overlay_reader = PdfReader(packet)

    with open('static/pdfs/input.pdf', "rb") as f:
        input_data = f.read()
    reader = PdfReader(BytesIO(input_data))

    writer = PdfWriter()
    overlay_page = overlay_reader.pages[0]

    for page in reader.pages:
        page.merge_page(overlay_page)
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output
