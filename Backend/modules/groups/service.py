from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas

from modules.students.service import delete_student as delete_single_student

def get_all_groups(db: Session) -> list[models.Group]:
    return db.query(models.Group).filter(models.Group.is_archive == False).all()

def get_group_by_id(db: Session, group_id: int) -> models.Group:
    db_group = db.query(models.Group).filter(
        models.Group.id_group == group_id,
        models.Group.is_archive == False
    ).first()
    
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена или находится в архиве")
    return db_group

def create_group(db: Session, group_data: schemas.GroupCreate) -> models.Group:
    existing = db.query(models.Group).filter(models.Group.group_name == group_data.group_name).first()
    if existing:
        if existing.is_archive:
            # Если группа существовала в архиве — восстанавливаем её активность
            existing.is_archive = False
            db.commit()
            db.refresh(existing)
            return existing
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Группа с таким названием уже существует")
    
    new_group = models.Group(group_name=group_data.group_name, is_archive=False)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

def update_group(db: Session, group_id: int, group_data: schemas.GroupUpdate) -> models.Group:
    db_group = db.query(models.Group).filter(models.Group.id_group == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена")
    
    try:
        # Если передано новое имя группы
        if group_data.group_name is not None:
            existing = db.query(models.Group).filter(models.Group.group_name == group_data.group_name).first()
            if existing and existing.id_group != group_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Это название группы уже занято")
            
            db_group.group_name = group_data.group_name

        # Если передан новый статус архивности
        if group_data.is_archive is not None:
            db_group.is_archive = group_data.is_archive
            
            # Каскадно меняем статус у всех студентов этой группы
            for student in db_group.students:
                student.is_archive = group_data.is_archive

        db.commit()
        db.refresh(db_group)
        return db_group

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при частичном обновлении данных группы: {str(e)}"
        )

def delete_group(db: Session, group_id: int) -> dict:
    # Ищем группу напрямую в базе данных (включая архивные, на случай повторного удаления)
    db_group = db.query(models.Group).filter(models.Group.id_group == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена")
        
    group_name = db_group.group_name
    current_students = list(db_group.students)
    
    has_archived_students = False
    
    try:
        for student in current_students:
            result = delete_single_student(db, student.id_student)
            if result.get("status") == "archived":
                has_archived_students = True

        if has_archived_students:
            # Если хотя бы один студент ушел в архив (так как был на экзамене)
            db_group.is_archive = True
            db.commit()
            return {
                "status": "archived",
                "message": f"Группа {group_name} содержит студентов с историей экзаменов. Группа и данные студенты перемещены в архив."
            }
        else:
            # Студентов либо не было, либо все они успешно стерлись физически
            db.delete(db_group)
            db.commit()
            return {
                "status": "deleted",
                "message": f"Группа {group_name} не связана с историей экзаменационных сессий и была полностью удалена."
            }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке каскадного удаления группы: {str(e)}"
        )