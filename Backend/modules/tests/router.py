from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.orm import joinedload
from urllib.parse import quote

from database import get_db
from modules.tests.models import Test
from modules.tests.schemas import TestCreate, TestUpdate, TestOut, TestIdOnly, TestGenerateRequest
from modules.disciplines.models import Discipline
from modules.questions.models import Question
from modules.tests.service import generate_balanced_tests
from .exporter import generate_tests_docx
from .exporter import generate_tests_pdf


router = APIRouter(
    prefix="/tests",
    tags=["Tests"]
)

# Получить вообще все билеты (для админки)
@router.get("/", response_model=List[TestOut], summary="Получить все билеты")
def get_all_tests(db: Session = Depends(get_db)):
    return db.query(Test).options(joinedload(Test.questions)).all()

# Получить номера билетов по конкретной дисциплине (по ID)
@router.get("/discipline/{discipline_id}", response_model=List[TestOut], summary="Получить билеты по дисциплине")
def get_tests_by_discipline(discipline_id: int, db: Session = Depends(get_db)):
    discipline_exists = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    
    if not discipline_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {discipline_id} не найдена"
        )
    
    tests = db.query(Test)\
        .options(joinedload(Test.questions))\
        .filter(Test.id_discipline == discipline_id)\
        .all()
        
    return tests

# Создать новый билет
@router.post("/", response_model=TestIdOnly, status_code=status.HTTP_201_CREATED, summary="Создать новый билет")
def create_test(test_data: TestCreate, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(
        Discipline.id_discipline == test_data.id_discipline
    ).first()
    
    if not discipline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {test_data.id_discipline} не найдена."
        )

    # Проверяем, не занят ли этот номер билета в данной дисциплине
    existing_test = db.query(Test).filter(
        Test.id_discipline == test_data.id_discipline,
        Test.test_number == test_data.test_number
    ).first()

    if existing_test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"В дисциплине '{discipline.name_discipline}' уже существует билет №{test_data.test_number}."
        )

    try:
        new_test = Test(
            test_number=test_data.test_number,
            id_discipline=test_data.id_discipline
        )

        if test_data.question_ids:
            questions = db.query(Question).filter(
                Question.id_question.in_(test_data.question_ids)
            ).all()

            if len(questions) != len(test_data.question_ids):
                raise HTTPException(status_code=404, detail="Некоторые вопросы не найдены")
            
            for q in questions:
                if q.id_discipline != test_data.id_discipline:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Вопрос ID {q.id_question} из другой дисциплины"
                    )

            # Привязываем вопросы к билету
            new_test.questions = questions

        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        return new_test
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при сохранении билета в базу данных."
        )
    
@router.patch("/{test_id}", response_model=TestOut, summary="Обновить билет и его вопросы")
def update_test(test_id: int, test_data: TestUpdate, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id_test == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Билет не найден")

    try:
        if test_data.test_number is not None:
            test.test_number = test_data.test_number
        
        if test_data.id_discipline is not None:
            disp = db.query(Discipline).filter(Discipline.id_discipline == test_data.id_discipline).first()
            if not disp:
                raise HTTPException(status_code=404, detail="Новая дисциплина не найдена")
            test.id_discipline = test_data.id_discipline

        # Обновляем вопросы
        if test_data.question_ids is not None:
            # Ищем новые вопросы
            new_questions = db.query(Question).filter(
                Question.id_question.in_(test_data.question_ids)
            ).all()

            # Валидация на количество
            if len(new_questions) != len(test_data.question_ids):
                raise HTTPException(status_code=404, detail="Некоторые ID вопросов не найдены")

            # Валидация на дисциплину (вопросы должны быть из той же дисциплины, что и билет)
            current_discipline_id = test.id_discipline
            for q in new_questions:
                if q.id_discipline != current_discipline_id:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Вопрос {q.id_question} не подходит к дисциплине билета"
                    )

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
    
# Удалить билет по ID
@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить билет по ID")
def delete_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id_test == test_id).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Билет с ID {test_id} не найден."
        )

    try:
        db.delete(test)
        db.commit()
        return None
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось удалить билет из-за ошибки базы данных."
        )
    
@router.post("/generate-confirm", response_model=List[TestOut], summary="Массовая генерация билетов")
def confirm_generated_tests(request: TestGenerateRequest, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id_discipline == request.id_discipline).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")

    questions_db = db.query(Question).filter(Question.id_discipline == request.id_discipline).all()
    if len(questions_db) < request.questions_per_test:
        raise HTTPException(status_code=400, detail="Недостаточно вопросов")

    try:
        generated_data = generate_balanced_tests(
            questions=questions_db,
            num_tests=request.num_tests,
            questions_per_test=request.questions_per_test
        )

        # Поиск свободных номеров
        occupied_numbers = db.query(Test.test_number).filter(
            Test.id_discipline == request.id_discipline
        ).all()
        occupied_set = {n[0] for n in occupied_numbers}

        available_numbers = []
        current_num = 1
        # Ищем номера, пока не наберем столько, сколько захотел пользователь
        while len(available_numbers) < request.num_tests:
            if current_num not in occupied_set:
                available_numbers.append(current_num)
            current_num += 1

        created_tests = []
        for i, item in enumerate(generated_data):
            assigned_number = available_numbers[i]
            
            new_test = Test(
                test_number=assigned_number,
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

    tests = db.query(Test).options(joinedload(Test.questions))\
        .filter(Test.id_discipline == discipline_id)\
        .order_by(Test.test_number).all()

    if not tests:
        raise HTTPException(status_code=404, detail="Билеты не найдены")

    # Генерируем документ
    file_stream = generate_tests_docx(discipline.name_discipline, tests)
    
    # --- ИСПРАВЛЕНИЕ ОШИБКИ ТУТ ---
    # Кодируем имя файла, чтобы избежать UnicodeEncodeError
    filename = f"Билеты_{discipline.name_discipline}.docx"
    encoded_filename = quote(filename) 
    
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            # Используем filename* для поддержки UTF-8 (русских букв)
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )

@router.get("/export/pdf/{discipline_id}", summary="Экспорт всех билетов дисциплины в PDF")
def export_tests_to_pdf(discipline_id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")

    tests = db.query(Test).options(joinedload(Test.questions))\
        .filter(Test.id_discipline == discipline_id)\
        .order_by(Test.test_number).all()

    if not tests:
        raise HTTPException(status_code=404, detail="Билеты не найдены")

    file_stream = generate_tests_pdf(discipline.name_discipline, tests)
    
    # Аналогичное исправление для PDF
    filename = f"Билеты_{discipline.name_discipline}.pdf"
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        file_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )