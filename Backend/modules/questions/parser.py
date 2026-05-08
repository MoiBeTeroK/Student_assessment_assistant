import re
import io
import fitz
from docx import Document

def parse_questions_from_file(file_content: bytes, file_type: str, discipline_name: str = None):
    if file_type == "docx":
        doc = Document(io.BytesIO(file_content))
        raw_lines = [para.text for para in doc.paragraphs]
    elif file_type == "pdf":
        pdf_file = fitz.open(stream=file_content, filetype="pdf")
        raw_lines = []
        for page in pdf_file:
            raw_lines.extend(page.get_text("text").splitlines())
    
    questions_text = []
    is_collecting = False
    
    # Регулярка для очистки
    number_prefix_pattern = re.compile(r'^\s*\d+[\.\)\s]+\s*')
    
    start_keywords = ["вопросы к экзамену", "вопросы к зачету", "перечень вопросов"]
    end_markers = ["литература", "источники", "материалы для", "утверждено", "составитель"]

    for line in raw_lines:
        text = line.strip()
        if not text: continue
        text_lower = text.lower()

        # Поиск старта
        if not is_collecting:
            if (discipline_name and discipline_name.lower() in text_lower) or \
               any(key in text_lower for key in start_keywords):
                is_collecting = True
                continue

        # Сбор данных
        if is_collecting:
            # Если встретили конец — выходим
            if any(marker in text_lower for marker in end_markers):
                break
            
            # Логика для DOCX: берем всё, что длиннее 15 символов
            if file_type == "docx":
                # Убираем цифры, если вдруг они вбиты руками, а не списком
                clean_question = number_prefix_pattern.sub('', text).strip()
                if len(clean_question) > 15:
                    # Проверка: не является ли строка названием дисциплины
                    if discipline_name and discipline_name.lower() in clean_question.lower():
                        continue
                    questions_text.append(clean_question)
            
            # Логика для PDF
            elif file_type == "pdf":
                question_pattern = re.compile(r'^\s*(\d+)[\.\)\s]+(.*)')
                match = question_pattern.match(text)
                if match:
                    content = match.group(2).strip()
                    if len(content) > 5:
                        questions_text.append(content)

    print(f"Обработано строк: {len(questions_text)}")

    return questions_text