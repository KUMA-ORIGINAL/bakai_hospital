from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode
from reportlab.lib.units import mm


def create_qr_code_in_memory(url):
    """Создает QR-код в памяти и возвращает BytesIO."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def create_pdf_with_qr_only(qr_url, organization, department, building, room):
    """Создаёт PDF с 2 QR-кодами и текстом вверху (организация, корпус, кабинет)."""
    qr_image_buffer = create_qr_code_in_memory(qr_url)
    qr_image = ImageReader(qr_image_buffer)

    page_width, _ = landscape(A4)

    gap = 30 * mm
    qr_width = 100 * mm
    qr_height = 100 * mm

    total_width = 2 * qr_width + gap
    start_x = (page_width - total_width) / 2

    x1 = start_x
    x2 = x1 + qr_width + gap
    y1 = y2 = 30 * mm

    buffer = BytesIO()
    can = canvas.Canvas(buffer, pagesize=landscape(A4))

    pdfmetrics.registerFont(TTFont('Roboto', 'static/fonts/Roboto.ttf'))

    # Позиции текста над QR-кодами
    text_offset_y = 20 * mm  # отступ от QR вверх
    line_spacing = 10 * mm  # межстрочный интервал

    can.setFont("Roboto", 16)
    can.drawCentredString(x1 + qr_width / 2, y1 + qr_height + text_offset_y + line_spacing * 3, organization)
    can.setFont("Roboto", 14)
    can.drawCentredString(x1 + qr_width / 2, y1 + qr_height + text_offset_y + line_spacing * 2,
                          f"Отделение: {department}")
    can.drawCentredString(x1 + qr_width / 2, y1 + qr_height + text_offset_y + line_spacing, f"Корпус: {building}")
    can.drawCentredString(x1 + qr_width / 2, y1 + qr_height + text_offset_y, f"Кабинет: {room}")

    # Второй QR
    can.setFont("Roboto", 16)
    can.drawCentredString(x2 + qr_width / 2, y2 + qr_height + text_offset_y + line_spacing * 3, organization)
    can.setFont("Roboto", 14)
    can.drawCentredString(x2 + qr_width / 2, y2 + qr_height + text_offset_y + line_spacing * 2,
                          f"Отделение: {department}")
    can.drawCentredString(x2 + qr_width / 2, y2 + qr_height + text_offset_y + line_spacing, f"Корпус: {building}")
    can.drawCentredString(x2 + qr_width / 2, y2 + qr_height + text_offset_y, f"Кабинет: {room}")

    # Добавляем 2 QR-кода
    can.drawImage(qr_image, x1, y1, width=qr_width, height=qr_height)
    can.drawImage(qr_image, x2, y2, width=qr_width, height=qr_height)

    can.save()
    buffer.seek(0)
    return buffer
