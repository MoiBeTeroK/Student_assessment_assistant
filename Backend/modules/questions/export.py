import io
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

# --- КОНСТАНТЫ ---
HEADER_TEXT = (
    "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n"
    "ФГБОУ ВО «Кубанский государственный университет»\n"
    "Кафедра вычислительных технологий\n"
)
FONT_NAME_DOCX = 'Times New Roman'
FONT_NAME_PDF = 'TimesNewRoman'

# --- КЛАСС PDF ---
class PDF(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        base_dir = os.getcwd()
        font_path = lambda f: os.path.join(base_dir, "static", "fonts", f)
        
        try:
            self.add_font(FONT_NAME_PDF, '', font_path("TIMES.TTF"), uni=True)
            self.add_font(FONT_NAME_PDF, 'B', font_path("TIMESBD.TTF"), uni=True)
        except Exception as e:
            # Если кириллица не поддерживается, FPDF упадет при печати
            print(f"Предупреждение: шрифты не загружены ({e})")

# --- ВСПОМОГАТЕЛЬНАЯ ЛОГИКА ---
def get_title(discipline_name):
    return f"Вопросы к экзамену по дисциплине\n«{discipline_name}»"

# --- ГЕНЕРАЦИЯ DOCX ---
def generate_docx(discipline_name: str, questions: list):
    doc = Document()
    
    # Настройка полей
    section = doc.sections[0]
    section.left_margin, section.right_margin = Cm(2), Cm(1)

    def add_para(text, size=12, bold=False, align=None, indent=0, space_after=0):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = FONT_NAME_DOCX
        run.font.size = Pt(size)
        run.bold = bold
        if align: p.alignment = align
        if indent: p.paragraph_format.first_line_indent = Cm(indent)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.0
        return p

    # 1. Шапка
    add_para(HEADER_TEXT, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    # 2. Заголовок
    add_para(get_title(discipline_name), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    # 3. Список вопросов
    for i, q_text in enumerate(questions, 1):
        add_para(f"{i}. {q_text}", indent=1.25, space_after=2)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# --- ГЕНЕРАЦИЯ PDF ---
# --- ГЕНЕРАЦИЯ PDF ---
def generate_pdf(discipline_name: str, questions: list):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Активируем жирный шрифт для шапки
    pdf.set_font(FONT_NAME_PDF, 'B', 11) # Можно 11 для компактности

    # 1. Шапка (h=4 вместо 5 сделает строки внутри шапки чуть ближе)
    pdf.multi_cell(0, 4, HEADER_TEXT, align="C")
    
    # --- МИНИМАЛЬНЫЙ ОТСТУП ---
    # Поставил 3мм. Если нужно ВПЛОТНУЮ, ставь 1 или 2.
    pdf.ln(3) 
    
    # 2. Заголовок
    # h=5 вместо 7 подтянет строки заголовка друг к другу
    pdf.multi_cell(0, 5, get_title(discipline_name), align="C")
    
    # Небольшой отступ перед списком вопросов
    pdf.ln(2)

    # 3. Вопросы
    pdf.set_font(FONT_NAME_PDF, '', 12)
    indent_width = 12.5  # 1.25 см
    
    for i, q_text in enumerate(questions, 1):
        # Используем l_margin для корректного позиционирования
        pdf.set_x(pdf.l_margin + indent_width) 
        pdf.multi_cell(0, 5, f"{i}. {q_text}")
        pdf.ln(1)

    # Генерация финального потока
    pdf_output = pdf.output()
    # Обработка разных версий fpdf2 (bytes vs bytearray)
    if isinstance(pdf_output, str):
        pdf_output = pdf_output.encode('latin-1')
        
    return io.BytesIO(pdf_output)