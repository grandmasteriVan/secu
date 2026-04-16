# --- FILE: app/services/pdf_service.py ---
import os
from fpdf import FPDF
from datetime import datetime

def create_certificate(user_name: str, course_title: str, filename: str):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    
    # Створюємо папки, якщо їх немає
    os.makedirs("static/certificates", exist_ok=True)
    os.makedirs("static/fonts", exist_ok=True)
    
    # Шлях до шрифту (потрібен для кирилиці)
    font_path = "static/fonts/DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", "", 16)
        font_name = "DejaVu"
    else:
        pdf.set_font("Arial", "", 16)
        font_name = "Arial"

    # Малюємо рамку
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(0.5)
    pdf.rect(13, 13, 271, 184)

    # Заголовок
    pdf.ln(30)
    pdf.set_font(font_name, "", 40)
    pdf.cell(0, 20, "СЕРТИФІКАТ", ln=True, align="C")
    pdf.set_font(font_name, "", 18)
    pdf.cell(0, 10, "ПРО ЗАКІНЧЕННЯ КУРСУ", ln=True, align="C")

    # Тіло сертифіката
    pdf.ln(20)
    pdf.set_font(font_name, "", 16)
    pdf.cell(0, 10, "Цим підтверджується, що", ln=True, align="C")
    
    pdf.ln(5)
    pdf.set_font(font_name, "", 30)
    pdf.cell(0, 20, user_name, ln=True, align="C")
    
    pdf.ln(5)
    pdf.set_font(font_name, "", 16)
    pdf.cell(0, 10, "успішно завершив(ла) курс:", ln=True, align="C")
    
    pdf.ln(5)
    pdf.set_font(font_name, "", 24)
    pdf.cell(0, 15, f"«{course_title}»", ln=True, align="C")

    # Футер (Дата та підпис)
    pdf.set_y(-50)
    date_str = datetime.now().strftime("%d.%m.%Y")
    pdf.set_font(font_name, "", 12)
    pdf.cell(100, 10, f"Дата: {date_str}", align="C")
    pdf.cell(0, 10, "SecuLearn AI Academy", align="C")

    file_path = f"static/certificates/{filename}"
    pdf.output(file_path)
    return file_path