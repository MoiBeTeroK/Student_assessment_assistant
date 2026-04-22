from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from Backend.database import get_db
from Backend.modules.tests.models import Test
from Backend.modules.tests.schemas import TestCreate, TestOut
from Backend.modules.disciplines.models import Discipline


router = APIRouter(
    prefix="/tests",
    tags=["tests"]
)

# Получить вообще все тесты (для админки)
@router.get("/", response_model=List[TestOut], summary="Получить все тесты")
def get_all_tests(db: Session = Depends(get_db)):
    return db.query(Test).all()

# Получить номера тестов по конкретной дисциплине (по ID)
@router.get("/discipline/{discipline_id}", response_model=List[TestOut], summary="Получить тесты по дисциплине")
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

# Создать новый тест
@router.post("/", response_model=TestOut, status_code=status.HTTP_201_CREATED, summary="Создать новый тест")
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

    # Проверяем, не занят ли этот номер теста в данной дисциплине
    existing_test = db.query(Test).filter(
        Test.id_discipline == test_data.id_discipline,
        Test.test_number == test_data.test_number
    ).first()

    if existing_test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"В дисциплине '{discipline.name_discipline}' уже существует тест №{test_data.test_number}."
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
            detail="Произошла ошибка при сохранении теста в базу данных."
        )
    
# Удалить тест по ID
@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить тест по ID")
def delete_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id_test == test_id).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тест с ID {test_id} не найден."
        )

    try:
        db.delete(test)
        db.commit()
        return None
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось удалить тест из-за ошибки базы данных."
        )