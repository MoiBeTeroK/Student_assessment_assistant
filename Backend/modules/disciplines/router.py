from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from . import schemas, service
from modules.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/disciplines",
    tags=["Disciplines"]
)


@router.post("/", response_model=schemas.DisciplineOut, summary="Создать новую дисциплину")
def create_discipline(
    discipline: schemas.DisciplineCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.create_discipline(db, discipline, current_user["user_id"])


@router.get("/", response_model=list[schemas.DisciplineOut], summary="Получить список дисциплин текущего пользователя")
def read_disciplines(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.get_all_disciplines(db, current_user["user_id"])


@router.get("/{discipline_id}", response_model=schemas.DisciplineOut, summary="Получить дисциплину по ID")
def read_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.get_discipline_by_id(db, discipline_id, current_user["user_id"])


@router.put("/{discipline_id}", response_model=schemas.DisciplineOut, summary="Изменить дисциплину")
def update_discipline(
    discipline_id: int,
    discipline: schemas.DisciplineCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.update_discipline(db, discipline_id, discipline, current_user["user_id"])


@router.delete("/{discipline_id}", summary="Удалить дисциплину")
def delete_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return service.delete_discipline(db, discipline_id, current_user["user_id"])
