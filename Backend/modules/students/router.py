from fastapi import APIRouter, Depends, status, UploadFile, File
from typing import List
from sqlalchemy.orm import Session

from database import get_db
from . import schemas, service

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

@router.post("/", response_model=schemas.StudentOut, summary="Добавить нового студента", deprecated=True)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return service.create_student(db, student)

@router.get("/", response_model=List[schemas.StudentOut], summary="Получить список всех студентов")
def read_students(db: Session = Depends(get_db)):
    return service.get_all_students(db)

@router.get("/{student_id}", response_model=schemas.StudentOut, summary="Получить студента по ID")
def read_student(student_id: int, db: Session = Depends(get_db)):
    return service.get_student_by_id(db, student_id)

@router.put("/{student_id}", response_model=schemas.StudentOut, summary="Обновить информацию о студенте")
def update_student(student_id: int, student_data: schemas.StudentUpdate, db: Session = Depends(get_db)):
    return service.update_student(db, student_id, student_data)

@router.delete("/{student_id}", summary="Удалить студента")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    return service.delete_student(db, student_id)

@router.patch("/batch", response_model=schemas.ImportResponse, summary="Массовое частичное обновление или создание")
def patch_students_batch(students_data: List[schemas.StudentImportSchema], db: Session = Depends(get_db)):
    return service.patch_students_batch(db, students_data)

@router.post("/import-from-file", response_model=schemas.ImportResponse, summary="Загрузить файл и сохранить")
async def import_from_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await service.import_from_file(db, file)