from fastapi import HTTPException, UploadFile, status
from typing import List
from sqlalchemy.orm import Session, joinedload

from . import models, schemas, parser_students
from modules.groups.models import Group

def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(
        name=student.name,
        id_group=student.id_group
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db.query(models.Student).options(joinedload(models.Student.group_rel)).filter(models.Student.id_student == db_student.id_student).first()

def get_all_students(db: Session) -> List[models.Student]:
    return db.query(models.Student).options(joinedload(models.Student.group_rel)).all()

def get_student_by_id(db: Session, student_id: int) -> models.Student:
    db_student = db.query(models.Student).options(joinedload(models.Student.group_rel)).filter(models.Student.id_student == student_id).first()
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден")
    return db_student

def update_student(db: Session, student_id: int, student_data: schemas.StudentUpdate) -> models.Student:
    db_student = db.query(models.Student).filter(models.Student.id_student == student_id).first()
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден")
    
    update_dict = student_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db.query(models.Student).options(joinedload(models.Student.group_rel)).filter(models.Student.id_student == student_id).first()

def delete_student(db: Session, student_id: int) -> dict:
    db_student = db.query(models.Student).filter(models.Student.id_student == student_id).first()
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден")
    
    db.delete(db_student)
    db.commit()
    return {"status": "success", "message": f"Студент с ID {student_id} удален"}

def patch_students_batch(db: Session, students_data: List[schemas.StudentImportSchema]) -> dict:
    result_students = []
    group_cache = {}

    for item in students_data:
        db_student = None
        if item.id_student:
            db_student = db.query(models.Student).filter_by(id_student=item.id_student).first()

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
            db_student = models.Student(name=item.name, id_group=target_group.id_group)
            db.add(db_student)
        
        db.flush()
        db_student.group_rel = target_group
        result_students.append(db_student)

    db.commit()
    return {"students": result_students}

async def import_from_file(db: Session, file: UploadFile) -> dict:
    filename = file.filename.lower()
    extension = "docx" if filename.endswith('.docx') else "pdf" if filename.endswith('.pdf') else None
    
    if not extension:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Разрешены только .docx и .pdf")

    try:
        content = await file.read()
        raw_data = parser_students.parse_students_from_content(extension, content)
        
        if not raw_data:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Студенты в файле не найдены")

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

            db_student = db.query(models.Student).filter_by(
                name=item["name"], 
                id_group=current_group.id_group
            ).first()

            if not db_student:
                db_student = models.Student(name=item["name"], id_group=current_group.id_group)
                db.add(db_student)
                db.flush()

            db_student.group_rel = current_group
            result_students.append(db_student)

        db.commit()
        return {"students": result_students}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при импорте: {str(e)}")
    finally:
        await file.close()

async def import_single_group_from_file(db: Session, file: UploadFile, target_group_name: str) -> dict:
    filename = file.filename.lower()
    extension = "docx" if filename.endswith('.docx') else "pdf" if filename.endswith('.pdf') else None
    
    if not extension:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Разрешены только .docx и .pdf")

    db_group = db.query(Group).filter_by(group_name=target_group_name).first()
    if not db_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Группа '{target_group_name}' не зарегистрирована в системе."
        )

    try:
        content = await file.read()
        raw_data = parser_students.parse_students_from_content(extension, content)
        
        filtered_students = [
            item for item in raw_data 
            if item["group"]["group_name"].strip().lower() == target_group_name.strip().lower()
        ]

        if not filtered_students:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail=f"В предоставленном файле не найдена группа '{target_group_name}' или в ней нет студентов."
            )

        result_students = []

        for item in filtered_students:
            db_student = db.query(models.Student).filter_by(
                name=item["name"], 
                id_group=db_group.id_group
            ).first()

            if not db_student:
                db_student = models.Student(name=item["name"], id_group=db_group.id_group)
                db.add(db_student)
                db.flush()

            db_student.group_rel = db_group
            result_students.append(db_student)

        db.commit()
        return {"students": result_students}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка при импорте группы: {str(e)}"
        )
    finally:
        await file.close()