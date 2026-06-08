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
    
    # Регулярка для очистки номеров вопросов в DOCX
    number_prefix_pattern = re.compile(r'^\s*\d+[\.\)\s]+\s*')
    # Регулярка для проверки заголовков в кавычках
    quotes_pattern = re.compile(r'^\s*[«"\'“].*[»"\'”]\s*$')
    # Регулярка для поиска начала вопроса в PDF (цифра в начале строки)
    pdf_question_start_pattern = re.compile(r'^\s*(\d+)[\.\)\s]+(.*)')
    
    start_keywords = ["вопросы к экзамену", "вопросы к зачету", "перечень вопросов"]
    end_markers = ["литература", "источники", "материалы для", "утверждено", "составитель"]

    lines_since_start = 0
    current_pdf_question = ""  # Буфер для сборки многострочного PDF-вопроса

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
            
            # Логика для DOCX
            if file_type == "docx":
                lines_since_start += 1

                if quotes_pattern.match(text):
                    continue
                
                if discipline_name and discipline_name.lower() in text_lower:
                    continue

                if lines_since_start == 1 and not re.match(r'^\s*\d+', text):
                    if not text.endswith(('.', '?', '!')):
                        continue

                clean_question = number_prefix_pattern.sub('', text).strip()
                if len(clean_question) > 15:
                    questions_text.append(clean_question)
            
            # Логика для PDF
            elif file_type == "pdf":
                match = pdf_question_start_pattern.match(text)
                
                if match:
                    # Если в буфере уже лежит предыдущий собранный вопрос, то сохраняем его перед началом нового
                    if current_pdf_question:
                        clean_q = current_pdf_question.strip()
                        if len(clean_q) > 5:
                            questions_text.append(clean_q)
                    
                    # Начинаем собирать новый вопрос (забираем группу без цифры)
                    current_pdf_question = match.group(2).strip()
                else:
                    # Если строка не начинается с цифры, это продолжение текущего вопроса
                    # Склеиваем её с буфером через пробел
                    if current_pdf_question:
                        current_pdf_question += " " + text
                    else:
                        # На случай, если название дисциплины или мусор попали до первого вопроса
                        if discipline_name and discipline_name.lower() in text_lower:
                            continue
                        # Пропускаем строки заголовков
                        if not text.endswith(('.', '?', '!')):
                            continue

    if file_type == "pdf" and current_pdf_question:
        clean_q = current_pdf_question.strip()
        if len(clean_q) > 5:
            questions_text.append(clean_q)

    print(f"Обработано строк: {len(questions_text)}")
    return questions_text