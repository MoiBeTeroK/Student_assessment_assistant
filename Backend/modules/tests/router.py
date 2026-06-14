from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from . import schemas, service

router = APIRouter(
    prefix="/tests",
    tags=["Tests"]
)

@router.get("/", response_model=List[schemas.TestOut], summary="Получить все билеты")
def get_all_tests(db: Session = Depends(get_db)):
    return service.get_all_tests(db)

@router.get("/discipline/{discipline_id}", response_model=List[schemas.TestOut], summary="Получить билеты по дисциплине")
def get_tests_by_discipline(discipline_id: int, db: Session = Depends(get_db)):
    return service.get_tests_by_discipline(db, discipline_id)

@router.post("/", response_model=schemas.TestIdOnly, status_code=status.HTTP_201_CREATED, summary="Создать новый билет")
def create_test(test_data: schemas.TestCreate, db: Session = Depends(get_db)):
    return service.create_test(db, test_data)
    
@router.patch("/{test_id}", response_model=schemas.TestOut, summary="Обновить билет и его вопросы")
def update_test(test_id: int, test_data: schemas.TestUpdate, db: Session = Depends(get_db)):
    return service.update_test(db, test_id, test_data)
    
@router.delete("/{test_id}", status_code=status.HTTP_200_OK, summary="Удалить билет по ID")
def delete_test(test_id: int, db: Session = Depends(get_db)):
    return service.delete_test(db, test_id)
    
@router.post("/generate-confirm", response_model=List[schemas.TestOut], summary="Массовая генерация билетов")
def confirm_generated_tests(request: schemas.TestGenerateRequest, db: Session = Depends(get_db)):
    return service.confirm_generated_tests(db, request)

@router.get("/export/tests/{discipline_id}", summary="Экспорт билетов в выбранном формате")
def export_tests_combined(
    discipline_id: int, 
    format: service.ExportFormat = Query(service.ExportFormat.docx, description="Формат файла (docx или pdf)"),
    db: Session = Depends(get_db)
):
    return service.export_tests_combined(db, discipline_id, format)