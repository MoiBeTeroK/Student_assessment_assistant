import io
import re
import fitz  # PyMuPDF
from docx import Document

def parse_students_from_content(file_extension: str, file_bytes: bytes):
    text = ""
    
    if file_extension == "docx":
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([p.text for p in doc.paragraphs])
    elif file_extension == "pdf":
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text() + "\n"

    students = []
    current_group = "Неизвестна"
    temp_ignore = False # Флаг для пропуска подгрупп
    
    group_regex = re.compile(r'(?i)(?:группа\s+([А-Я]{2}\d{2}(?:/\d+)?))|(([А-Я]{2}\d{2}(?:/\d+)?)\s+группа)')
    exclusions = ["Факультет", "Направление", "подгруппа"]

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 1. Поиск названия группы
        group_match = group_regex.search(line)
        if group_match:
            found_group = group_match.group(1) or group_match.group(2)
            found_group = re.sub(r'(?i)группа', '', found_group).strip()
            
            # Если это подгруппа (содержит /), включаем игнорирование
            if '/' in found_group:
                temp_ignore = True
                continue 
            
            # Если новая нормальная группа, выключаем игнорирование
            temp_ignore = False
            current_group = found_group
            continue
            
        # Пропускаем, если встретили слово "подгруппа" или флаг активен
        if "подгруппа" in line.lower() or temp_ignore:
            temp_ignore = True
            continue

        # 2. Обработка студента
        line_no_number = re.sub(r'^\d+[\.\)\s\t]+', '', line).strip()
        
        if len(line_no_number) < 5 or current_group == "Неизвестна":
            continue

        if line_no_number[0].isupper() and not any(ex in line_no_number for ex in exclusions):
            split_pattern = r'(?i)\s+[–—\-\(]|\s+зам\.|\s+староста|\s+бюджет|\s+договор|\s+госзаказ'
            clean_name = re.split(split_pattern, line_no_number)[0].strip()
            
            if len(clean_name.split()) >= 2:
                # ВАЖНО: Кладём просто строку в "group". 
                # Оборачивать в {"group_name": ...} будем в роутере или схеме.
                students.append({
                    "name": clean_name,
                    "group": current_group 
                })
            
    # Удаление дубликатов
    unique_students = []
    seen = set()

    for s in students:
        # Уникальность проверяем по ФИО + Название группы
        identifier = (s["name"], s["group"])
        if identifier not in seen:
            seen.add(identifier)
            # Формируем структуру, которую ждет StudentFileSchema
            unique_students.append({
                "name": s["name"],
                "group": {"group_name": s["group"]}
            })
            
    return unique_students