import io
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

class PDF(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.add_font('TimesNewRoman', '', 'static/fonts/TIMES.TTF', uni=True)
            self.add_font('TimesNewRoman', 'B', 'static/fonts/TIMESBD.TTF', uni=True)
        except Exception as e:
            print(f"Ошибка загрузки шрифтов: {e}")

    def header(self):
        # Оставляем пустым, чтобы шапка была только на первой странице
        pass

def generate_docx(discipline_name: str, questions: list):
    doc = Document()
    
    # Настройка полей страницы
    section = doc.sections[0]
    section.left_margin = Cm(2)
    section.right_margin = Cm(1)

    # Шапка
    header_para = doc.add_paragraph()
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_text = (
        "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n"
        "ФГБОУ ВО «Кубанский государственный университет»\n"
        "Кафедра вычислительных технологий"
    )
    run = header_para.add_run(header_text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)

    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(0)
    spacer.paragraph_format.line_spacing = 1.0

    # Заголовок
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_para.add_run(f"Вопросы к экзамену по дисциплине\n«{discipline_name}»")
    title_run.bold = True
    title_run.font.name = 'Times New Roman'
    title_run.font.size = Pt(12)

    for i, q_text in enumerate(questions, 1):
        p = doc.add_paragraph()
        
        # Убираем все внешние отступы
        p.paragraph_format.left_indent = 0
        # Отступ 1.25 см
        p.paragraph_format.first_line_indent = Cm(1.25)
        # Межстрочный интервал и отступ после
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.0
        
        q_run = p.add_run(f"{i}. {q_text}")
        q_run.font.name = 'Times New Roman'
        q_run.font.size = Pt(12)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def generate_pdf(discipline_name: str, questions: list):
    pdf = PDF()
    pdf.add_page()
    
    # Стандартный левый край
    left_margin = 10
    pdf.set_left_margin(left_margin)
    
    font_name = "TimesNewRoman" if "timesnewroman" in pdf.fonts else "Helvetica"
    
    # Шапка
    pdf.set_font(font_name, "B", 12)
    pdf.multi_cell(0, 5, 
        "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ\n"
        "ФГБОУ ВО «Кубанский государственный университет»\n"
        "Кафедра вычислительных технологий", 
        align="C")
    pdf.ln(10)
    
    pdf.multi_cell(0, 7, f"Вопросы к экзамену по дисциплине\n«{discipline_name}»", align="C")
    pdf.ln(5)

    pdf.set_font(font_name, "", 12)
    indent_width = 12.5  # 1.25 см
    
    for i, q_text in enumerate(questions, 1):
        text = f"{i}. {q_text}"
        
        # Печатаем отступ
        pdf.cell(indent_width)
        
        # Печатаем сам текст. 
        pdf.multi_cell(0, 5, text)
        
        # Интервал между вопросами
        pdf.ln(1)

    pdf_bytes = bytes(pdf.output())
    result = io.BytesIO(pdf_bytes)
    result.seek(0)
    return result