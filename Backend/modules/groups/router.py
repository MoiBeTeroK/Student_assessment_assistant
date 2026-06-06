from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from . import schemas, service

router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

@router.post("/", response_model=schemas.GroupOut, status_code=status.HTTP_201_CREATED, summary="Создать новую группу")
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    return service.create_group(db, group)

@router.get("/", response_model=list[schemas.GroupOut], summary="Получить список всех групп")
def read_groups(db: Session = Depends(get_db)):
    return service.get_all_groups(db)

@router.get("/{group_id}", response_model=schemas.GroupOut, summary="Получить информацию о группе по ID")
def read_group(group_id: int, db: Session = Depends(get_db)):
    return service.get_group_by_id(db, group_id)

@router.put("/{group_id}", response_model=schemas.GroupOut, summary="Обновить данные группы")
def update_group(group_id: int, group_data: schemas.GroupUpdate, db: Session = Depends(get_db)):
    return service.update_group(db, group_id, group_data)

@router.delete("/{group_id}", summary="Удалить группу")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    return service.delete_group(db, group_id)