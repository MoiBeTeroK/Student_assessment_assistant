from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from modules.questions.models import Question
from modules.disciplines.models import Discipline
from modules.results.models import ExamResult
from modules.questions.schemas import QuestionCreate, QuestionOut, QuestionPatch, QuestionBase
from modules.questions.parser import parse_questions_from_file
from modules.questions.export import generate_docx, generate_pdf
import urllib.parse

router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)

@router.post("/", response_model=List[QuestionOut], status_code=status.HTTP_201_CREATED, summary="Создать новый вопрос")
def create_questions_bulk(questions_data: List[QuestionCreate], db: Session = Depends(get_db)):
    if not questions_data:
        raise HTTPException(status_code=400, detail="Список вопросов пуст")

    discipline_id = questions_data[0].id_discipline
    discipline = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Дисциплина с ID {discipline_id} не найдена.")

    new_questions_objects = []
    skipped_count = 0

    for item in questions_data:
        # Проверка на дубликат внутри базы
        existing_question = db.query(Question).filter(
            Question.id_discipline == item.id_discipline,
            Question.question_content == item.question_content
        ).first()

        if existing_question:
            skipped_count += 1
            continue

        new_question = Question(**item.model_dump())
        new_questions_objects.append(new_question)

    if not new_questions_objects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Все вопросы из списка уже существуют в базе или список некорректен."
        )

    try:
        db.add_all(new_questions_objects)
        db.commit()
        for q in new_questions_objects:
            db.refresh(q)

        return new_questions_objects
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка при сохранении списка вопросов."
        )
    
@router.get("/", response_model=List[QuestionOut], summary="Получить все вопросы")
def get_all_questions(db: Session = Depends(get_db)):
    return db.query(Question).all()

@router.get("/discipline/{discipline_id}", response_model=List[QuestionOut], summary="Получить вопросы по дисциплине")
def get_questions_by_discipline(discipline_id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    
    if not discipline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {discipline_id} не найдена."
        )
    questions = db.query(Question).filter(Question.id_discipline == discipline_id).all()
    return questions

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить вопрос по ID")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id_question == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопрос с ID {question_id} не найден."
        )

    try:
        db.delete(question)
        db.commit()

        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении вопроса из базы данных."
        )

@router.delete("/clear-discipline/{id_discipline}", status_code=status.HTTP_200_OK,summary="Удалить все вопросы из конкретной дисциплины")
def clear_questions_by_discipline(id_discipline: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id_discipline == id_discipline).first()
    if not discipline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Дисциплина с ID {id_discipline} не найдена"
        )

    try:
        # Находим все вопросы этой дисциплины
        query = db.query(Question).filter(Question.id_discipline == id_discipline)
        count = query.count() # Считаем, сколько удалим для отчета
        query.delete(synchronize_session=False)
        db.commit()

        return {
            "message": f"Все вопросы дисциплины '{discipline.name_discipline}' успешно удалены",
            "deleted_count": count
        }
    except Exception as e:
        db.rollback()
        print(f"Ошибка при очистке вопросов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при удалении вопросов"
        )
    
@router.patch("/{question_id}", response_model=QuestionOut, summary="Частично изменить вопрос")
def patch_question(question_id: int, updated_data: QuestionPatch, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id_question == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопрос с ID {question_id} не найден."
        )

    # Проверка диапазона для complexity_score, если значение передано, проверяем его
    if updated_data.complexity_score is not None:
        if not (0.1 <= updated_data.complexity_score <= 1.0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недопустимое значение сложности: {updated_data.complexity_score}. Должно быть от 0.1 до 1.0."
            )

    # Проверка дисциплины (если меняется)
    if updated_data.id_discipline is not None:
        discipline = db.query(Discipline).filter(Discipline.id_discipline == updated_data.id_discipline).first()
        if not discipline:
            raise HTTPException(status_code=404, detail="Дисциплина не найдена.")

    # Проверка на дубликат (если меняется контент или дисциплина)
    if updated_data.question_content or updated_data.id_discipline:
        check_content = updated_data.question_content or question.question_content
        check_discipline = updated_data.id_discipline or question.id_discipline
        
        duplicate = db.query(Question).filter(
            Question.id_discipline == check_discipline,
            Question.question_content == check_content,
            Question.id_question != question_id
        ).first()

        if duplicate:
            raise HTTPException(status_code=400, detail="Такой вопрос уже существует.")

    update_dict = updated_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(question, key, value)

    try:
        db.commit()
        db.refresh(question)
        return question
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении в базу.")
    
@router.post("/parse-preview/{id_discipline}", response_model=List[QuestionBase], summary="Предварительный просмотр вопросов из файла")
async def preview_questions_from_file(id_discipline: int, file: UploadFile = File(...),db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id_discipline == id_discipline).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")

    # Определяем тип файла
    ext = file.filename.split('.')[-1].lower()
    if ext not in ['docx', 'pdf']:
        raise HTTPException(status_code=400, detail="Поддерживаются только .docx и .pdf")

    try:
        content = await file.read()
        raw_questions = parse_questions_from_file(content, ext, discipline.name_discipline)
        
        preview_data = [
            {
                "id_discipline": id_discipline,
                "question_content": text,
                "standard_answer": None,
                "complexity_score": None
            }
            for text in raw_questions
        ]
        return preview_data
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке файла: {str(e)}")
    
@router.get("/export/{id_discipline}")
def export_questions(
    id_discipline: int, 
    format: str = "docx", 
    db: Session = Depends(get_db)
):
    # 1. Получаем дисциплину и вопросы
    discipline = db.query(Discipline).filter(Discipline.id_discipline == id_discipline).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")
    
    questions = db.query(Question).filter(Question.id_discipline == id_discipline).all()
    question_texts = [q.question_content for q in questions]
    
    if not question_texts:
        raise HTTPException(status_code=400, detail="В дисциплине нет вопросов для экспорта")

    # 2. Генерация файла
    filename_base = f"Список_вопросов_{discipline.name_discipline.replace(' ', '_')}"
    
    if format.lower() == "docx":
        file_stream = generate_docx(discipline.name_discipline, question_texts)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{filename_base}.docx"
    elif format.lower() == "pdf":
        file_stream = generate_pdf(discipline.name_discipline, question_texts)
        media_type = "application/pdf"
        filename = f"{filename_base}.pdf"
    else:
        raise HTTPException(status_code=400, detail="Неверный формат. Используйте docx или pdf")

    # 3. Кодируем имя файла для корректной передачи кириллицы
    encoded_filename = urllib.parse.quote(filename)
    
    return StreamingResponse(
        file_stream,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )