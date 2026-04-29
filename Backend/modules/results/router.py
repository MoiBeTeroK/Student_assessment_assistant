from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from Backend.database import get_db
from Backend.modules.results.models import ExamResult
from Backend.modules.results.schemas import ExamResultCreate, ExamResultOut
from Backend.modules.students.models import Student
from Backend.modules.tests.models import Test

router = APIRouter(
    prefix="/results",
    tags=["Results"]
)

@router.post("/", response_model=ExamResultOut, status_code=status.HTTP_201_CREATED, summary="Сохранить результат экзамена")
def create_exam_result(result_data: ExamResultCreate, db: Session = Depends(get_db)):
    # 1. Проверяем, существует ли студент
    student = db.query(Student).filter(Student.id_student == result_data.id_student).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {result_data.id_student} не найден."
        )

    # 2. Проверяем, существует ли тест
    test = db.query(Test).filter(Test.id_test == result_data.id_test).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тест с ID {result_data.id_test} не найден."
        )

    # 3. Создаем запись (поле date уже есть в result_data и попадет в модель автоматически)
    new_result = ExamResult(**result_data.model_dump())
    
    try:
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        return new_result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при сохранении результата в базу данных."
        )

@router.get("/student/{student_id}", response_model=List[ExamResultOut], summary="Получить все результаты студента")
def get_student_results(student_id: int, db: Session = Depends(get_db)):
    student_exists = db.query(Student).filter(Student.id_student == student_id).first()
    if not student_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден"
        )
        
    results = db.query(ExamResult).filter(ExamResult.id_student == student_id).all()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"У студента с ID {student_id} пока нет сохраненных результатов"
        )
        
    return results

@router.get("/{result_id}", response_model=ExamResultOut, summary="Получить конкретный результат по ID")
def get_result_by_id(result_id: int, db: Session = Depends(get_db)):
    result = db.query(ExamResult).filter(ExamResult.id_result == result_id).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Результат с ID {result_id} не найден"
        )
    return result