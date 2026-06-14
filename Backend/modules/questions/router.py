from fastapi import APIRouter, Depends, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from . import schemas, service

router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)

@router.post("/", response_model=List[schemas.QuestionOut], status_code=status.HTTP_201_CREATED, summary="Создать новый вопрос", deprecated=True)
def create_questions_bulk(questions_data: List[schemas.QuestionCreate], db: Session = Depends(get_db)):
    return service.create_questions_bulk(db, questions_data)

@router.get("/", response_model=List[schemas.QuestionOut], summary="Получить все вопросы")
def get_all_questions(db: Session = Depends(get_db)):
    return service.get_all_questions(db)

@router.get("/discipline/{discipline_id}", response_model=List[schemas.QuestionOut], summary="Получить вопросы по дисциплине")
def get_questions_by_discipline(discipline_id: int, db: Session = Depends(get_db)):
    return service.get_questions_by_discipline(db, discipline_id)

@router.delete("/{question_id}", status_code=status.HTTP_200_OK, summary="Удалить вопрос по ID")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    return service.delete_question(db, question_id)

@router.delete("/clear-discipline/{id_discipline}", status_code=status.HTTP_200_OK, summary="Удалить все вопросы из конкретной дисциплины")
def clear_questions_by_discipline(id_discipline: int, db: Session = Depends(get_db)):
    return service.clear_questions_by_discipline(db, id_discipline)
    
@router.patch("/batch", response_model=List[schemas.QuestionOut], summary="Массовое частичное обновление или создание вопросов")
def patch_questions_batch(questions_data: List[schemas.QuestionImportSchema], db: Session = Depends(get_db)):
    return service.patch_questions_batch(db, questions_data)
    
@router.post("/parse-preview/{id_discipline}", response_model=List[schemas.QuestionBase], summary="Предварительный просмотр вопросов из файла")
async def preview_questions_from_file(id_discipline: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    return service.preview_questions_from_file(db, id_discipline, file.filename, content)
    
@router.get("/export/{id_discipline}", summary="Экспорт списка вопросов в выбранном формате")
def export_questions(
    id_discipline: int, 
    format: service.ExportFormat = Query(service.ExportFormat.docx, description="Формат файла (docx или pdf)"), 
    db: Session = Depends(get_db)
):
    return service.export_questions(db, id_discipline, format)