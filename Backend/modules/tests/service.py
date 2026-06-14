from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from urllib.parse import quote
from enum import Enum

from . import models, schemas, generator, exporter
from modules.disciplines.models import Discipline
from modules.questions.models import Question
from modules.results.models import ExamResult

class ExportFormat(str, Enum):
    docx = "docx"
    pdf = "pdf"

def get_all_tests(db: Session) -> List[models.Test]:
    return db.query(models.Test).options(joinedload(models.Test.questions)).filter(models.Test.is_archive == False).all()

def get_tests_by_discipline(db: Session, discipline_id: int) -> List[models.Test]:
    discipline_exists = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    if not discipline_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {discipline_id} не найдена"
        )
    # Возвращаем только активные билеты конкретной дисциплины
    return db.query(models.Test)\
        .options(joinedload(models.Test.questions))\
        .filter(
            models.Test.id_discipline == discipline_id,
            models.Test.is_archive == False
        ).all()

def create_test(db: Session, test_data: schemas.TestCreate) -> models.Test:
    discipline = db.query(Discipline).filter(
        Discipline.id_discipline == test_data.id_discipline
    ).first()
    
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Дисциплина с ID {test_data.id_discipline} не найдена.")

    existing_test = db.query(models.Test).filter(
        models.Test.id_discipline == test_data.id_discipline,
        models.Test.test_number == test_data.test_number
    ).first()

    if existing_test:
        # Если билет существовал, но был отправлен в архив, то можно его "реанимировать" с новыми данными
        if existing_test.is_archive:
            existing_test.is_archive = False
            if test_data.question_ids:
                questions = db.query(Question).filter(Question.id_question.in_(test_data.question_ids)).all()
                existing_test.questions = questions
            db.commit()
            db.refresh(existing_test)
            return existing_test
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"В дисциплине '{discipline.name_discipline}' уже существует активный билет №{test_data.test_number}."
        )

    try:
        new_test = models.Test(
            test_number=test_data.test_number,
            id_discipline=test_data.id_discipline,
            is_archive=False
        )

        if test_data.question_ids:
            questions = db.query(Question).filter(Question.id_question.in_(test_data.question_ids)).all()

            if len(questions) != len(test_data.question_ids):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Некоторые вопросы не найдены")
            
            for q in questions:
                if q.id_discipline != test_data.id_discipline:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Вопрос из другой дисциплины")

            new_test.questions = questions

        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        return new_test
        
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при сохранении билета.")

def update_test(db: Session, test_id: int, test_data: schemas.TestUpdate) -> models.Test:
    test = db.query(models.Test).filter(models.Test.id_test == test_id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Билет не найден")

    try:
        if test_data.test_number is not None:
            test.test_number = test_data.test_number
        
        if test_data.id_discipline is not None:
            if not db.query(Discipline).filter(Discipline.id_discipline == test_data.id_discipline).first():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Новая дисциплина не найдена")
            test.id_discipline = test_data.id_discipline

        if test_data.is_archive is not None:
            test.is_archive = test_data.is_archive

        if test_data.question_ids is not None:
            new_questions = db.query(Question).filter(Question.id_question.in_(test_data.question_ids)).all()

            if len(new_questions) != len(test_data.question_ids):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Некоторые ID вопросов не найдены")

            for q in new_questions:
                if q.id_discipline != test.id_discipline:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Вопрос {q.id_question} не подходит к дисциплине")

            test.questions = new_questions

        db.commit()
        db.refresh(test)
        return test
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при обновлении: {str(e)}")

def delete_test(db: Session, test_id: int) -> dict:
    test = db.query(models.Test).filter(models.Test.id_test == test_id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Билет с ID {test_id} не найден.")

    # Проверяем связь билета с таблицей результатов экзаменов
    has_exam_results = db.query(ExamResult).filter(ExamResult.id_test == test_id).first() is not None

    try:
        if has_exam_results:
            # Экзамен по этому билету уже сдавался - мягкое удаление (в архив)
            test.is_archive = True
            db.commit()
            return {
                "status": "archived",
                "message": f"Билет связан с результатами экзаменов студентов. Он успешно перемещен в архив."
            }
        else:
            # Экзаменов нет - полное физическое удаление из базы данных
            db.delete(test)
            db.commit()
            return {
                "status": "deleted",
                "message": f"Билет не содержит результатов и успешно полностью удален из базы."
            }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Не удалось обработать удаление билета: {str(e)}"
        )

def confirm_generated_tests(db: Session, request: schemas.TestGenerateRequest) -> List[models.Test]:
    discipline = db.query(Discipline).filter(Discipline.id_discipline == request.id_discipline).first()
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дисциплина не найдена")

    # Для генерации билетов берем только активные (не архивные) вопросы
    questions_db = db.query(Question).filter(
        Question.id_discipline == request.id_discipline,
        Question.is_archive == False
    ).all()
    
    if len(questions_db) < request.questions_per_test:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недостаточно активных вопросов в базе")

    try:
        generated_data = generator.generate_balanced_tests(
            questions=questions_db,
            num_tests=request.num_tests,
            questions_per_test=request.questions_per_test
        )

        # Выбираем занятые номера только среди активных билетов
        occupied_numbers = db.query(models.Test.test_number).filter(
            models.Test.id_discipline == request.id_discipline,
            models.Test.is_archive == False
        ).all()
        occupied_set = {n[0] for n in occupied_numbers}

        available_numbers = []
        current_num = 1
        while len(available_numbers) < request.num_tests:
            if current_num not in occupied_set:
                available_numbers.append(current_num)
            current_num += 1

        created_tests = []
        for i, item in enumerate(generated_data):
            new_test = models.Test(
                test_number=available_numbers[i],
                id_discipline=request.id_discipline,
                is_archive=False
            )
            for q_obj in item["questions"]:
                new_test.questions.append(q_obj)
            
            db.add(new_test)
            created_tests.append(new_test)
        
        db.commit()
        for t in created_tests:
            db.refresh(t)

        return created_tests
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка сохранения: {str(e)}")

def export_tests_combined(db: Session, discipline_id: int, format: ExportFormat) -> StreamingResponse:
    discipline = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дисциплина не найдена")

    # Экспортируем только активные билеты
    tests = db.query(models.Test).options(joinedload(models.Test.questions))\
        .filter(
            models.Test.id_discipline == discipline_id,
            models.Test.is_archive == False
        )\
        .order_by(models.Test.test_number).all()

    if not tests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Активные билеты не найдены для экспорта")

    export_config = {
        ExportFormat.docx: {
            "generator": exporter.generate_tests_docx,
            "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "extension": "docx"
        },
        ExportFormat.pdf: {
            "generator": exporter.generate_tests_pdf,
            "media_type": "application/pdf",
            "extension": "pdf"
        }
    }

    current_settings = export_config[format]
    
    file_stream = current_settings["generator"](
        discipline.name_discipline, 
        tests
    )
    safe_discipline_name = discipline.name_discipline.replace(' ', '_')
    filename_encoded = quote(f"Билеты_{safe_discipline_name}.{current_settings['extension']}")
    
    return StreamingResponse(
        file_stream,
        media_type=current_settings["media_type"],
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"
        }
    )