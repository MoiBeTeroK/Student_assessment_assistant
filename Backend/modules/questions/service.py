from fastapi import HTTPException, status, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from urllib.parse import quote
from typing import List
from enum import Enum

from modules.disciplines.models import Discipline

from modules.tests.models import test_questions, Test
from modules.results.models import ExamResult
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
            # Если вопрос существовал, но был в архиве — восстанавливаем его
            if existing_question.is_archive:
                existing_question.is_archive = False
                new_questions_objects.append(existing_question)
            continue

        new_question = models.Question(**item.model_dump())
        new_questions_objects.append(new_question)

    if not new_questions_objects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Все вопросы из списка уже существуют в базе и активны."
        )

    try:
        db.add_all([q for q in new_questions_objects if q.id_question is None])  # Добавляем только новые
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
    return db.query(models.Question).filter(models.Question.is_archive == False).all()

def get_questions_by_discipline(db: Session, discipline_id: int) -> List[models.Question]:
    discipline = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    if not discipline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {discipline_id} не найдена."
        )
    # Выбираем только активные вопросы для конкретной дисциплины
    return db.query(models.Question).filter(
        models.Question.id_discipline == discipline_id,
        models.Question.is_archive == False
    ).all()

def delete_question(db: Session, question_id: int) -> dict:
    question = db.query(models.Question).filter(models.Question.id_question == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопрос с ID {question_id} не найден."
        )

    related_ticket_ids = [
        r.id_test for r in db.query(test_questions.c.id_test).filter(
            test_questions.c.id_question == question_id
        ).all()
    ]

    try:
        if related_ticket_ids:
            has_exam_results = db.query(ExamResult).filter(
                ExamResult.id_test.in_(related_ticket_ids)
            ).first() is not None

            if has_exam_results:
                # Билет с этим вопросом уже сдавался - мягкое удаление (в архив)
                question.is_archive = True
                db.commit()
                return {
                    "status": "archived",
                    "message": f"Вопрос входит в состав билетов, по которым уже приняты экзамены. Он успешно перемещен в архив."
                }
            else:
                # Билет есть, но результатов по нему нет - запрет удаления
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Невозможно удалить вопрос, так как он привязан к существующему экзаменационному билету. Сначала удалите или отредактируйте билет."
                )
        else:
            # Вопрос не привязан ни к одному билету - полное физическое удаление
            db.delete(question)
            db.commit()
            return {
                "status": "deleted",
                "message": f"Вопрос успешно полностью удален из базы данных."
            }
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке удаления вопроса: {str(e)}"
        )

def clear_questions_by_discipline(db: Session, id_discipline: int) -> dict:
    discipline = db.query(Discipline).filter(Discipline.id_discipline == id_discipline).first()
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Дисциплина с ID {id_discipline} не найдена")

    try:
        questions = db.query(models.Question).filter(models.Question.id_discipline == id_discipline).all()
        
        deleted_count = 0
        archived_count = 0
        skipped_count = 0

        for q in questions:
            related_ticket_ids = [
                r.id_test for r in db.query(test_questions.c.id_test).filter(
                    test_questions.c.id_question == q.id_question
                ).all()
            ]
            
            if related_ticket_ids:
                has_exam_results = db.query(ExamResult).filter(
                    ExamResult.id_test.in_(related_ticket_ids)
                ).first() is not None
                
                if has_exam_results:
                    q.is_archive = True
                    archived_count += 1
                else:
                    skipped_count += 1
            else:
                db.delete(q)
                deleted_count += 1
                
        db.commit()

        return {
            "message": f"Обработка очистки дисциплины '{discipline.name_discipline}' завершена.",
            "completely_deleted": deleted_count,
            "moved_to_archive": archived_count,
            "skipped_due_to_active_tickets": skipped_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Произошла ошибка при очистке вопросов дисциплины: {str(e)}"
        )
    
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
                
                # Если обновляем существующий архивный вопрос — восстанавливаем его активность
                db_question.is_archive = False
            else:
                existing = db.query(models.Question).filter(
                    models.Question.question_content == item.question_content,
                    models.Question.id_discipline == item.id_discipline
                ).first()
                
                if existing:
                    existing.is_archive = False  # Вытаскиваем из архива, если отправлен повторно
                    result_questions.append(existing)
                    continue

                db_question = models.Question(**item.model_dump(exclude_unset=True, exclude={'id_question'}))
                db_question.is_archive = False
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
    
    # Экспортируем только активные вопросы
    questions = db.query(models.Question).filter(
        models.Question.id_discipline == id_discipline,
        models.Question.is_archive == False
    ).all()
    
    if not questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="В дисциплине нет активных вопросов для экспорта")

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