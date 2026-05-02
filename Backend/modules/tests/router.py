from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.orm import joinedload

from database import get_db
from modules.tests.models import Test
from modules.tests.schemas import TestCreate, TestUpdate, TestOut, TestIdOnly
from modules.disciplines.models import Discipline
from modules.questions.models import Question


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
    # Проверяем, существует ли такая дисциплина вообще
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

        # ДОБАВЬ ЭТОТ БЛОК:
        if test_data.question_ids:
            # Ищем вопросы в базе
            questions = db.query(Question).filter(
                Question.id_question.in_(test_data.question_ids)
            ).all()

            # Проверка: все ли вопросы нашлись?
            if len(questions) != len(test_data.question_ids):
                raise HTTPException(status_code=404, detail="Некоторые вопросы не найдены")
            
            # Валидация: принадлежат ли вопросы этой дисциплине?
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
    # 1. Ищем существующий билет
    test = db.query(Test).filter(Test.id_test == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Билет не найден")

    try:
        # 2. Если пришел новый номер билета или дисциплина — обновляем
        if test_data.test_number is not None:
            test.test_number = test_data.test_number
        
        if test_data.id_discipline is not None:
            # Проверяем, существует ли новая дисциплина
            disp = db.query(Discipline).filter(Discipline.id_discipline == test_data.id_discipline).first()
            if not disp:
                raise HTTPException(status_code=404, detail="Новая дисциплина не найдена")
            test.id_discipline = test_data.id_discipline

        # 3. Обновляем вопросы (перезаписываем список)
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

            # Перезаписываем связь (SQLAlchemy сама удалит старые записи в связующей таблице и добавит новые)
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