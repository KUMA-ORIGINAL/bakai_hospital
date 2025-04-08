from reportlab.lib.pagesizes import A4, landscape
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


def create_pdf_with_qr_only(qr_url):
    """Создаёт чистый PDF с QR-кодами (без текста и без шаблонов)."""
    qr_image_buffer = create_qr_code_in_memory(qr_url)
    qr_image = ImageReader(qr_image_buffer)

    qr_width = 70 * mm
    qr_height = 70 * mm
    x1 = 39 * mm
    y1 = 100 * mm
    x2 = x1 * 3 + qr_height + 1 * mm
    y2 = y1

    buffer = BytesIO()
    can = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Добавляем 2 QR-кода
    can.drawImage(qr_image, x1, y1, width=qr_width, height=qr_height)
    can.drawImage(qr_image, x2, y2, width=qr_width, height=qr_height)

    can.save()
    buffer.seek(0)
    return buffer