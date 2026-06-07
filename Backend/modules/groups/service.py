from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas

def get_all_groups(db: Session) -> list[models.Group]:
    return db.query(models.Group).all()

def get_group_by_id(db: Session, group_id: int) -> models.Group:
    db_group = db.query(models.Group).filter(models.Group.id_group == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена")
    return db_group

def create_group(db: Session, group_data: schemas.GroupCreate) -> models.Group:
    db_group = db.query(models.Group).filter(models.Group.group_name == group_data.group_name).first()
    if db_group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Группа с таким названием уже существует")
    
    new_group = models.Group(group_name=group_data.group_name)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

def update_group(db: Session, group_id: int, group_data: schemas.GroupUpdate) -> models.Group:
    db_group = get_group_by_id(db, group_id)
    
    if group_data.group_name:
        existing = db.query(models.Group).filter(models.Group.group_name == group_data.group_name).first()
        if existing and existing.id_group != group_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Это название группы уже занято")
        
        db_group.group_name = group_data.group_name

    db.commit()
    db.refresh(db_group)
    return db_group

def delete_group(db: Session, group_id: int) -> dict:
    db_group = get_group_by_id(db, group_id)
    group_name = db_group.group_name
    db.delete(db_group)
    db.commit()
    return {"status": "success", "message": f"Группа {group_name} удалена"}