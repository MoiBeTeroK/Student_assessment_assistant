from fastapi import HTTPException, status, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from urllib.parse import quote
from typing import List
from enum import Enum

from modules.disciplines.models import Discipline
from . import models, schemas, parser, export

class ExportFormat(str, Enum):
    docx = "docx"
    pdf = "pdf"

def create_questions_bulk(db: Session, questions_data: List[schemas.QuestionCreate]) -> List[models.Question]:
    if not questions_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Список вопросов пуст")

    discipline_id = questions_data[0].id_discipline
    discipline = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Дисциплина с ID {discipline_id} не найдена.")

    new_questions_objects = []

    for item in questions_data:
        existing_question = db.query(models.Question).filter(
            models.Question.id_discipline == item.id_discipline,
            models.Question.question_content == item.question_content
        ).first()

        if existing_question:
            continue

        new_question = models.Question(**item.model_dump())
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
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка при сохранении списка вопросов."
        )

def get_all_questions(db: Session) -> List[models.Question]:
    return db.query(models.Question).all()

def get_questions_by_discipline(db: Session, discipline_id: int) -> List[models.Question]:
    discipline = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    
    if not discipline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {discipline_id} не найдена."
        )
    return db.query(models.Question).filter(models.Question.id_discipline == discipline_id).all()

def delete_question(db: Session, question_id: int) -> None:
    question = db.query(models.Question).filter(models.Question.id_question == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопрос с ID {question_id} не найден."
        )

    try:
        db.delete(question)
        db.commit()
        return None
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении вопроса из базы данных."
        )

def clear_questions_by_discipline(db: Session, id_discipline: int) -> dict:
    discipline = db.query(Discipline).filter(Discipline.id_discipline == id_discipline).first()
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Дисциплина с ID {id_discipline} не найдена")

    try:
        query = db.query(models.Question).filter(models.Question.id_discipline == id_discipline)
        count = query.count()
        query.delete(synchronize_session=False)
        db.commit()

        return {
            "message": f"Все вопросы дисциплины '{discipline.name_discipline}' успешно удалены",
            "deleted_count": count
        }
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Произошла ошибка при удалении вопросов")

def patch_questions_batch(db: Session, questions_data: List[schemas.QuestionImportSchema]) -> List[models.Question]:
    if not questions_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Список данных пуст")

    result_questions = []
    
    try:
        for item in questions_data:
            db_question = None
            
            if item.id_question:
                db_question = db.query(models.Question).filter(
                    models.Question.id_question == item.id_question
                ).first()

            if db_question:
                update_data = item.model_dump(exclude_unset=True, exclude={'id_question'})
                
                if 'question_content' in update_data or 'id_discipline' in update_data:
                    new_content = update_data.get('question_content', db_question.question_content)
                    new_disc_id = update_data.get('id_discipline', db_question.id_discipline)
                    
                    duplicate = db.query(models.Question).filter(
                        models.Question.question_content == new_content,
                        models.Question.id_discipline == new_disc_id,
                        models.Question.id_question != db_question.id_question
                    ).first()
                    
                    if duplicate:
                        continue

                for key, value in update_data.items():
                    setattr(db_question, key, value)
            else:
                existing = db.query(models.Question).filter(
                    models.Question.question_content == item.question_content,
                    models.Question.id_discipline == item.id_discipline
                ).first()
                
                if existing:
                    result_questions.append(existing)
                    continue

                db_question = models.Question(**item.model_dump(exclude_unset=True, exclude={'id_question'}))
                db.add(db_question)

            db.flush()
            result_questions.append(db_question)
        db.commit()
        for q in result_questions:
            db.refresh(q)
        return result_questions
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка при массовой обработке: {str(e)}"
        )

def preview_questions_from_file(db: Session, id_discipline: int, file_filename: str, content: bytes) -> List[dict]:
    discipline = db.query(Discipline).filter(Discipline.id_discipline == id_discipline).first()
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дисциплина не найдена")

    ext = file_filename.split('.')[-1].lower()
    if ext not in ['docx', 'pdf']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Поддерживаются только .docx и .pdf")

    try:
        raw_questions = parser.parse_questions_from_file(content, ext, discipline.name_discipline)
        
        return [
            {
                "id_discipline": id_discipline,
                "question_content": text,
                "standard_answer": None,
                "complexity_score": None
            }
            for text in raw_questions
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при обработке файла: {str(e)}")

def export_questions(db: Session, id_discipline: int, format: ExportFormat) -> StreamingResponse:
    discipline = db.query(Discipline).filter(Discipline.id_discipline == id_discipline).first()
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дисциплина не найдена")
    
    questions = db.query(models.Question).filter(models.Question.id_discipline == id_discipline).all()
    if not questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="В дисциплине нет вопросов для экспорта")

    question_texts = [q.question_content for q in questions]

    export_settings = {
        ExportFormat.docx: {
            "generator": export.generate_docx,
            "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "ext": "docx"
        },
        ExportFormat.pdf: {
            "generator": export.generate_pdf,
            "media_type": "application/pdf",
            "ext": "pdf"
        }
    }

    settings = export_settings[format]
    file_stream = settings["generator"](discipline.name_discipline, question_texts)
    
    filename = quote(f"Вопросы_{discipline.name_discipline.replace(' ', '_')}.{settings['ext']}")
    
    return StreamingResponse(
        file_stream,
        media_type=settings["media_type"],
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )