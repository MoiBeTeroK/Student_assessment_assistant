from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from Backend.database import get_db
from . import models, schemas

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

# Создать студента
@router.post("/", response_model=schemas.StudentOut, summary="Добавить нового студента")
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Добавляет студента в базу. 
    Валидация на дубликаты отключена — можно добавлять одинаковых.
    """
    db_student = models.Student(
        name=student.name,
        group=student.group
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# Получить всех студентов
@router.get("/", response_model=list[schemas.StudentOut], summary="Получить список всех студентов")
def read_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

# Получить студента по ID
@router.get("/{student_id}", response_model=schemas.StudentOut, summary="Получить студента по ID")
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id_student == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return db_student

# Изменить данные студента
@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, student_data: schemas.StudentUpdate, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id_student == student_id).first()
    
    if not db_student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    update_dict = student_data.dict(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student

# Удалить студента
@router.delete("/{student_id}", summary="Удалить студента")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id_student == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    db.delete(db_student)
    db.commit()
    return {"status": "success", "message": f"Студент с ID {student_id} удален"}