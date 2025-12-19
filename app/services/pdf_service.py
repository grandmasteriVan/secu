import os
from fpdf import FPDF
from datetime import datetime

class PDFService(FPDF):
    def header(self):
        # Цей метод викликається автоматично при створенні сторінки
        pass

    def footer(self):
        # Позиція 1.5 см знизу
        self.set_y(-15)
        #self.set_font("ukr_font", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'SecuLearn AI Generated Certificate - {datetime.now().year}', align='C')

def create_certificate(user_name: str, course_name: str, output_filename: str = "certificate.pdf"):
    """
    Генерує PDF сертифікат і зберігає його.
    Повертає повний шлях до файлу.
    """
    
    # 1. Налаштування шляхів (щоб працювало і на Windows, і на Linux)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # папка app/
    FONT_PATH = os.path.join(BASE_DIR, "fonts", "Roboto-Regular.ttf") # Шлях до шрифту
    OUTPUT_DIR = os.path.join(BASE_DIR, "static", "certificates")
    
    # Створюємо папку для сертифікатів, якщо її немає
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    full_output_path = os.path.join(OUTPUT_DIR, output_filename)

    # 2. Ініціалізація PDF (Альбомна орієнтація - 'L')
    pdf = PDFService(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    # 3. Реєстрація українського шрифту
    # ВАЖЛИВО: Без цього кирилиця буде знаками питання
    try:
        pdf.add_font("ukr_font", "", FONT_PATH)
        pdf.set_font("ukr_font", "", 16)

    except FileNotFoundError:
        print(f"ERROR: Шрифт не знайдено за шляхом {FONT_PATH}. Використовую стандартний (кирилиця не працюватиме).")
        pdf.set_font("Arial", "", 16)

    pdf.set_font("Arial", "", 16)
    
    # --- ДИЗАЙН ---

    # 4. Рамка
    pdf.set_draw_color(106, 92, 255) # Колір SecuLearn (фіолетовий)
    pdf.set_line_width(1.5)
    pdf.rect(10, 10, 277, 190) # Рамка навколо сторінки

    # 5. Заголовок "СЕРТИФІКАТ"
    pdf.ln(20) # Відступ зверху
    pdf.set_font("ukr_font", "", 40)
    pdf.set_text_color(106, 92, 255)
    pdf.cell(0, 20, "СЕРТИФІКАТ", align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Підзаголовок
    pdf.set_font("ukr_font", "", 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "про проходження навчання", align='C', new_x="LMARGIN", new_y="NEXT")

    pdf.ln(20) # Відступ

    # 6. Текст "Цим засвідчується, що"
    pdf.set_font("ukr_font", "", 14)
    pdf.cell(0, 10, "Цим засвідчується, що", align='C', new_x="LMARGIN", new_y="NEXT")

    # 7. Ім'я студента (Велике)
    pdf.ln(5)
    pdf.set_font("ukr_font", "", 32)
    pdf.set_text_color(0, 0, 0) # Чорний
    pdf.cell(0, 20, user_name, align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Лінія під ім'ям
    x_center = pdf.w / 2
    pdf.line(x_center - 60, pdf.get_y(), x_center + 60, pdf.get_y())

    pdf.ln(10)

    # 8. Текст про курс
    pdf.set_font("ukr_font", "", 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "успішно завершив(ла) курс з кібербезпеки:", align='C', new_x="LMARGIN", new_y="NEXT")

    # 9. Назва курсу
    pdf.ln(5)
    pdf.set_font("ukr_font", "", 24)
    pdf.set_text_color(106, 92, 255)
    pdf.cell(0, 15, course_name, align='C', new_x="LMARGIN", new_y="NEXT")

    # 10. Дата та підпис
    pdf.ln(25)
    pdf.set_font("ukr_font", "", 12)
    pdf.set_text_color(50, 50, 50)
    
    # Використовуємо таблицю для дати (зліва) і підпису (справа)
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    # Зліва (Дата)
    pdf.set_x(40)
    pdf.cell(60, 10, f"Дата видачі: {current_date}", align='L')
    
    # Справа (Підпис)
    pdf.set_x(200)
    pdf.cell(60, 10, "SecuLearn AI Team", align='R')

    # Збереження файлу
    pdf.output(full_output_path)
    
    return full_output_path