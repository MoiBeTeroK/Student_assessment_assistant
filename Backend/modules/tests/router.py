from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from urllib.parse import quote

from database import get_db

from . import models, schemas, generator, exporter

from modules.disciplines.models import Discipline
from modules.questions.models import Question

router = APIRouter(
    prefix="/tests",
    tags=["Tests"]
)

@router.get("/", response_model=List[schemas.TestOut], summary="Получить все билеты")
def get_all_tests(db: Session = Depends(get_db)):
    return db.query(models.Test).options(joinedload(models.Test.questions)).all()

@router.get("/discipline/{discipline_id}", response_model=List[schemas.TestOut], summary="Получить билеты по дисциплине")
def get_tests_by_discipline(discipline_id: int, db: Session = Depends(get_db)):
    discipline_exists = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    
    if not discipline_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {discipline_id} не найдена"
        )
    
    return db.query(models.Test)\
        .options(joinedload(models.Test.questions))\
        .filter(models.Test.id_discipline == discipline_id)\
        .all()

@router.post("/", response_model=schemas.TestIdOnly, status_code=status.HTTP_201_CREATED, summary="Создать новый билет")
def create_test(test_data: schemas.TestCreate, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(
        Discipline.id_discipline == test_data.id_discipline
    ).first()
    
    if not discipline:
        raise HTTPException(status_code=404, detail=f"Дисциплина с ID {test_data.id_discipline} не найдена.")

    # Проверяем номер билета
    existing_test = db.query(models.Test).filter(
        models.Test.id_discipline == test_data.id_discipline,
        models.Test.test_number == test_data.test_number
    ).first()

    if existing_test:
        raise HTTPException(
            status_code=400,
            detail=f"В дисциплине '{discipline.name_discipline}' уже существует билет №{test_data.test_number}."
        )

    try:
        new_test = models.Test(
            test_number=test_data.test_number,
            id_discipline=test_data.id_discipline
        )

        if test_data.question_ids:
            questions = db.query(Question).filter(Question.id_question.in_(test_data.question_ids)).all()

            if len(questions) != len(test_data.question_ids):
                raise HTTPException(status_code=404, detail="Некоторые вопросы не найдены")
            
            for q in questions:
                if q.id_discipline != test_data.id_discipline:
                    raise HTTPException(status_code=400, detail=f"Вопрос ID {q.id_question} из другой дисциплины")

            new_test.questions = questions

        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        return new_test
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении билета.")
    
@router.patch("/{test_id}", response_model=schemas.TestOut, summary="Обновить билет и его вопросы")
def update_test(test_id: int, test_data: schemas.TestUpdate, db: Session = Depends(get_db)):
    test = db.query(models.Test).filter(models.Test.id_test == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Билет не найден")

    try:
        if test_data.test_number is not None:
            test.test_number = test_data.test_number
        
        if test_data.id_discipline is not None:
            if not db.query(Discipline).filter(Discipline.id_discipline == test_data.id_discipline).first():
                raise HTTPException(status_code=404, detail="Новая дисциплина не найдена")
            test.id_discipline = test_data.id_discipline

        # Обновляем вопросы
        if test_data.question_ids is not None:
            new_questions = db.query(Question).filter(Question.id_question.in_(test_data.question_ids)).all()

            if len(new_questions) != len(test_data.question_ids):
                raise HTTPException(status_code=404, detail="Некоторые ID вопросов не найдены")

            for q in new_questions:
                if q.id_discipline != test.id_discipline:
                    raise HTTPException(status_code=400, detail=f"Вопрос {q.id_question} не подходит к дисциплине")

            test.questions = new_questions

        db.commit()
        db.refresh(test)
        return test
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении: {str(e)}")
    
@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить билет по ID")
def delete_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(models.Test).filter(models.Test.id_test == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail=f"Билет с ID {test_id} не найден.")

    try:
        db.delete(test)
        db.commit()
        return None
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Не удалось удалить билет.")
    
@router.post("/generate-confirm", response_model=List[schemas.TestOut], summary="Массовая генерация билетов")
def confirm_generated_tests(request: schemas.TestGenerateRequest, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id_discipline == request.id_discipline).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")

    questions_db = db.query(Question).filter(Question.id_discipline == request.id_discipline).all()
    if len(questions_db) < request.questions_per_test:
        raise HTTPException(status_code=400, detail="Недостаточно вопросов")

    try:
        generated_data = generator.generate_balanced_tests(
            questions=questions_db,
            num_tests=request.num_tests,
            questions_per_test=request.questions_per_test
        )

        occupied_numbers = db.query(models.Test.test_number).filter(
            models.Test.id_discipline == request.id_discipline
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
                id_discipline=request.id_discipline
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
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения: {str(e)}")
    
@router.get("/export/docx/{discipline_id}", summary="Экспорт всех билетов дисциплины в DOCX")
def export_tests_to_docx(discipline_id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")

    tests = db.query(models.Test).options(joinedload(models.Test.questions))\
        .filter(models.Test.id_discipline == discipline_id)\
        .order_by(models.Test.test_number).all()

    if not tests:
        raise HTTPException(status_code=404, detail="Билеты не найдены")

    file_stream = exporter.generate_tests_docx(discipline.name_discipline, tests)
    filename = quote(f"Билеты_{discipline.name_discipline}.docx")
    
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )

@router.get("/export/pdf/{discipline_id}", summary="Экспорт всех билетов дисциплины в PDF")
def export_tests_to_pdf(discipline_id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")

    tests = db.query(models.Test).options(joinedload(models.Test.questions))\
        .filter(models.Test.id_discipline == discipline_id)\
        .order_by(models.Test.test_number).all()

    if not tests:
        raise HTTPException(status_code=404, detail="Билеты не найдены")

    file_stream = exporter.generate_tests_pdf(discipline.name_discipline, tests)
    filename = quote(f"Билеты_{discipline.name_discipline}.pdf")
    
    return StreamingResponse(
        file_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )