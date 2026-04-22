from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from Backend.database import get_db
from Backend.modules.tests.models import Test
from Backend.modules.tests.schemas import TestCreate, TestOut, TestQuestionLink
from Backend.modules.disciplines.models import Discipline
from Backend.modules.questions.models import Question


router = APIRouter(
    prefix="/tests",
    tags=["tests"]
)

# Получить вообще все билеты (для админки)
@router.get("/", response_model=List[TestOut], summary="Получить все билеты")
def get_all_tests(db: Session = Depends(get_db)):
    return db.query(Test).all()

# Получить номера билетов по конкретной дисциплине (по ID)
@router.get("/discipline/{discipline_id}", response_model=List[TestOut], summary="Получить билеты по дисциплине")
def get_tests_by_discipline(discipline_id: int, db: Session = Depends(get_db)):
    # Проверяем, существует ли дисциплина
    discipline_exists = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    
    if not discipline_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {discipline_id} не найдена"
        )
    
    tests = db.query(Test).filter(Test.id_discipline == discipline_id).all()
    return tests

# Создать новый билет
@router.post("/", response_model=TestOut, status_code=status.HTTP_201_CREATED, summary="Создать новый билет")
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
        db.add(new_test)
        db.commit()
        db.refresh(new_test)
        return new_test
        
    except Exception as e:
        db.rollback() # Откатываем изменения, если что-то пошло не так
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при сохранении билета в базу данных."
        )
    
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
    
@router.post("/add-question", summary="Добавить вопрос в билет")
def add_question_to_test(link: TestQuestionLink, db: Session = Depends(get_db)):
    # Проверяем, существуют ли такие билет и вопрос
    test = db.query(Test).filter(Test.id_test == link.id_test).first()
    question = db.query(Question).filter(Question.id_question == link.id_question).first()
    
    if not test or not question:
        raise HTTPException(status_code=404, detail="Билет или вопрос не найден")

    # Проверяем, из одной ли они дисциплины
    if test.id_discipline != question.id_discipline:
        raise HTTPException(status_code=400, detail="Дисциплины билета и вопроса не совпадают")

    # Если вопроса еще нет в тесте — добавляем
    if question not in test.questions:
        test.questions.append(question)
        db.commit()
        return {"status": "success", "message": f"Вопрос {link.id_question} добавлен в билет {link.id_test}"}
    
    return {"status": "info", "message": "Вопрос уже привязан к этому билету"}

@router.delete("/remove-question", summary="Удалить вопрос из билета")
def remove_question_from_test(link: TestQuestionLink, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id_test == link.id_test).first()
    question = db.query(Question).filter(Question.id_question == link.id_question).first()

    if test and question in test.questions:
        test.questions.remove(question)
        db.commit()
        return {"status": "success", "message": "Вопрос удален из билета"}
    
    raise HTTPException(status_code=404, detail="Связь не найдена")