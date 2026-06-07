from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from . import models, schemas
from modules.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/disciplines",
    tags=["Disciplines"]
)


def _get_own_discipline(discipline_id: int, owner_id: int, db: Session) -> models.Discipline:
    discipline = db.query(models.Discipline).filter(
        models.Discipline.id_discipline == discipline_id,
        models.Discipline.owner_id == owner_id,
    ).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Дисциплина не найдена")
    return discipline


@router.post("/", response_model=schemas.DisciplineOut, summary="Создать новую дисциплину")
def create_discipline(
    discipline: schemas.DisciplineCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner_id = current_user["user_id"]
    clean_name = discipline.name_discipline.strip()
    existing = db.query(models.Discipline).filter(
        func.lower(models.Discipline.name_discipline) == func.lower(clean_name),
        models.Discipline.owner_id == owner_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Дисциплина с названием '{clean_name}' уже существует"
        )
    db_discipline = models.Discipline(name_discipline=clean_name, owner_id=owner_id)
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)
    return db_discipline


@router.get("/", response_model=list[schemas.DisciplineOut], summary="Получить список дисциплин текущего пользователя")
def read_disciplines(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner_id = current_user["user_id"]
    return db.query(models.Discipline).filter(models.Discipline.owner_id == owner_id).all()


@router.get("/{discipline_id}", response_model=schemas.DisciplineOut, summary="Получить дисциплину по ID")
def read_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return _get_own_discipline(discipline_id, current_user["user_id"], db)


@router.put("/{discipline_id}", response_model=schemas.DisciplineOut, summary="Изменить дисциплину")
def update_discipline(
    discipline_id: int,
    discipline: schemas.DisciplineCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner_id = current_user["user_id"]
    db_discipline = _get_own_discipline(discipline_id, owner_id, db)

    duplicate = db.query(models.Discipline).filter(
        func.lower(models.Discipline.name_discipline) == func.lower(discipline.name_discipline),
        models.Discipline.owner_id == owner_id,
        models.Discipline.id_discipline != discipline_id,
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="Другая дисциплина уже использует это название")

    db_discipline.name_discipline = discipline.name_discipline
    db.commit()
    db.refresh(db_discipline)
    return db_discipline


@router.delete("/{discipline_id}", summary="Удалить дисциплину")
def delete_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_discipline = _get_own_discipline(discipline_id, current_user["user_id"], db)
    db.delete(db_discipline)
    db.commit()
    return {"status": "success", "message": "Discipline deleted"}
