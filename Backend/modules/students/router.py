from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from sqlalchemy.orm import Session, joinedload
from database import get_db
from . import models, schemas, parser_students
from modules.groups.models import Group
from modules.students.models import Student

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

@router.post("/", response_model=schemas.StudentOut, summary="Добавить нового студента", deprecated=True)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(
        name=student.name,
        id_group=student.id_group
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db.query(Student).options(joinedload(Student.group_rel)).filter(Student.id_student == db_student.id_student).first()

@router.get("/", response_model=List[schemas.StudentOut], summary="Получить список всех студентов")
def read_students(db: Session = Depends(get_db)):
    return db.query(Student).options(joinedload(Student.group_rel)).all()

@router.get("/{student_id}", response_model=schemas.StudentOut, summary="Получить студента по ID")
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).options(joinedload(Student.group_rel)).filter(Student.id_student == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return db_student

@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, student_data: schemas.StudentUpdate, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id_student == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    update_dict = student_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db.query(Student).options(joinedload(Student.group_rel)).filter(Student.id_student == student_id).first()

@router.delete("/{student_id}", summary="Удалить студента")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id_student == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    db.delete(db_student)
    db.commit()
    return {"status": "success", "message": f"Студент с ID {student_id} удален"}

@router.patch("/batch", response_model=schemas.ImportResponse, summary="Массовое частичное обновление или создание")
def patch_students_batch(students_data: List[schemas.StudentImportSchema], db: Session = Depends(get_db)):
    result_students = []
    group_cache = {}

    for item in students_data:
        db_student = None
        if item.id_student:
            db_student = db.query(Student).filter_by(id_student=item.id_student).first()

        # Поиск или создание группы
        g_name = item.group.group_name
        if g_name not in group_cache:
            db_group = db.query(Group).filter_by(group_name=g_name).first()
            if not db_group:
                db_group = Group(group_name=g_name)
                db.add(db_group)
                db.flush()
            group_cache[g_name] = db_group
        
        target_group = group_cache[g_name]

        if db_student:
            if item.name: db_student.name = item.name
            db_student.id_group = target_group.id_group
        else:
            db_student = Student(name=item.name, id_group=target_group.id_group)
            db.add(db_student)
        
        db.flush()
        db_student.group_rel = target_group
        result_students.append(db_student)

    db.commit()
    return {"students": result_students}

@router.post("/import-from-file", response_model=schemas.ImportResponse, summary="Загрузить файл и сохранить")
async def import_from_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = file.filename.lower()
    extension = "docx" if filename.endswith('.docx') else "pdf" if filename.endswith('.pdf') else None
    
    if not extension:
        raise HTTPException(status_code=400, detail="Разрешены только .docx и .pdf")

    try:
        content = await file.read()
        raw_data = parser_students.parse_students_from_content(extension, content)
        
        if not raw_data:
            raise HTTPException(status_code=422, detail="Студенты в файле не найдены")

        result_students = []
        group_cache = {}

        for item in raw_data:
            g_name = item["group"]["group_name"]
            
            if g_name not in group_cache:
                db_group = db.query(Group).filter_by(group_name=g_name).first()
                if not db_group:
                    db_group = Group(group_name=g_name)
                    db.add(db_group)
                    db.flush()
                group_cache[g_name] = db_group
            
            current_group = group_cache[g_name]

            # Поиск дубликата
            db_student = db.query(Student).filter_by(
                name=item["name"], 
                id_group=current_group.id_group
            ).first()

            if not db_student:
                db_student = Student(name=item["name"], id_group=current_group.id_group)
                db.add(db_student)
                db.flush()

            db_student.group_rel = current_group
            result_students.append(db_student)

        db.commit()
        return {"students": result_students}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при импорте: {str(e)}")
    finally:
        await file.close()