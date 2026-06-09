from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from . import schemas, service

router = APIRouter(
    prefix="/results",
    tags=["Results"]
)

@router.post("/calculate", response_model=schemas.CalculationResponse, summary="Рассчитать предварительную оценку")
def calculate_results(data: schemas.CalculateExamRequest, db: Session = Depends(get_db)):
    return service.calculate_results(db, data)

@router.get("/student/{student_id}", response_model=List[schemas.ExamResultOut], summary="Получить результаты студента")
def get_student_results(student_id: int, db: Session = Depends(get_db)):
    return service.get_student_results(db, student_id)

@router.get("/{result_id}", response_model=schemas.ExamResultOut, summary="Получить конкретный результат по ID")
def get_result_by_id(result_id: int, db: Session = Depends(get_db)):
    return service.get_result_by_id(db, result_id)

@router.post("/start", response_model=schemas.ExamStartResponse, status_code=status.HTTP_201_CREATED, summary="Начать экзамен")
def start_exam(data: schemas.ExamResultCreate, db: Session = Depends(get_db)):
    return service.start_exam(db, data)
    
@router.put("/{id_result}/final-grade", response_model=schemas.ExamResultOut, summary="Установить финальную оценку")
def set_final_grade(id_result: int, data: schemas.FinalGradePut, db: Session = Depends(get_db)):
    return service.set_final_grade(db, id_result, data)
    
@router.get("/analytics/group/{group_id}/discipline/{discipline_id}", response_model=schemas.GroupAnalyticsOut, summary="Вывод аналитики")
def get_group_analytics(group_id: int, discipline_id: int, db: Session = Depends(get_db)):
    return service.get_group_analytics(db, group_id, discipline_id)

@router.get("/filter/discipline/{discipline_id}/year/{year}", response_model=List[schemas.ExamResultOut], summary="Получить результаты по дисциплине и году")
def get_results_by_discipline_and_year(discipline_id: int, year: int, db: Session = Depends(get_db)):
    return service.get_results_by_discipline_and_year(db, discipline_id, year)