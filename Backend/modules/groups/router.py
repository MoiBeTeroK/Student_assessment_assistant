from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from . import models, schemas

router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

@router.post("/", response_model=schemas.GroupOut, status_code=status.HTTP_201_CREATED, summary="Создать новую группу")
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    db_group = db.query(models.Group).filter(models.Group.group_name == group.group_name).first()
    if db_group:
        raise HTTPException(status_code=400, detail="Группа с таким названием уже существует")
    
    new_group = models.Group(group_name=group.group_name)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

@router.get("/", response_model=list[schemas.GroupOut], summary="Получить список всех групп")
def read_groups(db: Session = Depends(get_db)):
    return db.query(models.Group).all()

@router.get("/{group_id}", response_model=schemas.GroupOut, summary="Получить информацию о группе по ID")
def read_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(models.Group).filter(models.Group.id_group == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return db_group

@router.put("/{group_id}", response_model=schemas.GroupOut, summary="Обновить данные группы")
def update_group(group_id: int, group_data: schemas.GroupUpdate, db: Session = Depends(get_db)):
    db_group = db.query(models.Group).filter(models.Group.id_group == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    
    if group_data.group_name:
        existing = db.query(models.Group).filter(models.Group.group_name == group_data.group_name).first()
        if existing and existing.id_group != group_id:
            raise HTTPException(status_code=400, detail="Это название группы уже занято")
        db_group.group_name = group_data.group_name

    db.commit()
    db.refresh(db_group)
    return db_group

@router.delete("/{group_id}", summary="Удалить группу")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(models.Group).filter(models.Group.id_group == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    
    db.delete(db_group)
    db.commit()
    return {"status": "success", "message": f"Группа {db_group.group_name} удалена"}