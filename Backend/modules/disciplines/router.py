from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from . import models, schemas
from sqlalchemy import func

router = APIRouter(
    prefix="/disciplines",
    tags=["Disciplines"]
)

# Создать дисциплину
@router.post("/", response_model=schemas.DisciplineOut, summary="Создать новую дисциплину")
def create_discipline(discipline: schemas.DisciplineCreate, db: Session = Depends(get_db)):
    clean_name = discipline.name_discipline.strip()
    existing_db = db.query(models.Discipline).filter(
        func.lower(models.Discipline.name_discipline) == func.lower(clean_name)
    ).first()
    if existing_db:
        raise HTTPException(
            status_code=400, 
            detail=f"Дисциплина с названием '{clean_name}' уже существует"
        )

    db_discipline = models.Discipline(name_discipline=clean_name)
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)
    return db_discipline

@router.get("/", response_model=list[schemas.DisciplineOut], summary="Получить список всех дисциплин")
def read_disciplines(db: Session = Depends(get_db)):
    return db.query(models.Discipline).all()

@router.get("/{discipline_id}", response_model=schemas.DisciplineOut, summary="Получить дисциплину по ID")
def read_discipline(discipline_id: int, db: Session = Depends(get_db)):
    db_discipline = db.query(models.Discipline).filter(models.Discipline.id_discipline == discipline_id).first()
    if not db_discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")
    return db_discipline

@router.put("/{discipline_id}", response_model=schemas.DisciplineOut, summary="Изменить дисциплину")
def update_discipline(discipline_id: int, discipline: schemas.DisciplineCreate, db: Session = Depends(get_db)):
    db_discipline = db.query(models.Discipline).filter(models.Discipline.id_discipline == discipline_id).first()
    if not db_discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")
    
    duplicate_discipline = db.query(models.Discipline).filter(
        models.Discipline.name_discipline == discipline.name_discipline,
        models.Discipline.id_discipline != discipline_id
    ).first()
    if duplicate_discipline:
        raise HTTPException(
            status_code=400, 
            detail="Другая дисциплина уже использует это название"
        )
    
    db_discipline.name_discipline = discipline.name_discipline
    db.commit()
    db.refresh(db_discipline)
    return db_discipline

@router.delete("/{discipline_id}", summary="Удалить дисциплину")
def delete_discipline(discipline_id: int, db: Session = Depends(get_db)):
    db_discipline = db.query(models.Discipline).filter(models.Discipline.id_discipline == discipline_id).first()
    if not db_discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")
    
    db.delete(db_discipline)
    db.commit()
    return {"status": "success", "message": "Discipline deleted"}