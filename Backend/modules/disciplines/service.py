from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from . import models, schemas

def create_discipline(db: Session, discipline: schemas.DisciplineCreate) -> models.Discipline:
    clean_name = discipline.name_discipline.strip()
    existing_db = db.query(models.Discipline).filter(
        func.lower(models.Discipline.name_discipline) == func.lower(clean_name)
    ).first()
    if existing_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Дисциплина с названием '{clean_name}' уже существует"
        )

    db_discipline = models.Discipline(name_discipline=clean_name)
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)
    return db_discipline

def get_all_disciplines(db: Session) -> List[models.Discipline]:
    return db.query(models.Discipline).all()

def get_discipline_by_id(db: Session, discipline_id: int) -> models.Discipline:
    db_discipline = db.query(models.Discipline).filter(models.Discipline.id_discipline == discipline_id).first()
    if not db_discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дисциплина не найдена")
    return db_discipline

def update_discipline(db: Session, discipline_id: int, discipline: schemas.DisciplineCreate) -> models.Discipline:
    db_discipline = db.query(models.Discipline).filter(models.Discipline.id_discipline == discipline_id).first()
    if not db_discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дисциплина не найдена")
    
    duplicate_discipline = db.query(models.Discipline).filter(
        models.Discipline.name_discipline == discipline.name_discipline,
        models.Discipline.id_discipline != discipline_id
    ).first()
    if duplicate_discipline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Другая дисциплина уже использует это название"
        )
    
    db_discipline.name_discipline = discipline.name_discipline
    db.commit()
    db.refresh(db_discipline)
    return db_discipline

def delete_discipline(db: Session, discipline_id: int) -> dict:
    db_discipline = db.query(models.Discipline).filter(models.Discipline.id_discipline == discipline_id).first()
    if not db_discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дисциплина не найдена")
    
    db.delete(db_discipline)
    db.commit()
    return {"status": "success", "message": "Discipline deleted"}