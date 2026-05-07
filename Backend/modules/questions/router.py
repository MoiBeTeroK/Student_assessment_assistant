from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from modules.questions.models import Question
from modules.disciplines.models import Discipline
from modules.questions.schemas import QuestionCreate, QuestionOut, QuestionPatch

router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)

@router.post("/", response_model=QuestionOut, status_code=status.HTTP_201_CREATED, summary="Создать новый вопрос")
def create_question(question_data: QuestionCreate, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(
        Discipline.id_discipline == question_data.id_discipline
    ).first()
    
    if not discipline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {question_data.id_discipline} не найдена. Невозможно создать вопрос."
        )

    # Проверка, нет ли уже такого же вопроса в этой дисциплине
    existing_question = db.query(Question).filter(
        Question.id_discipline == question_data.id_discipline,
        Question.question_content == question_data.question_content
    ).first()

    if existing_question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой вопрос уже существует в данной дисциплине."
        )

    new_question = Question(**question_data.model_dump())
    
    try:
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        return new_question
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка при сохранении вопроса."
        )
    
@router.get("/", response_model=List[QuestionOut], summary="Получить все вопросы")
def get_all_questions(db: Session = Depends(get_db)):
    return db.query(Question).all()

@router.get("/discipline/{discipline_id}", response_model=List[QuestionOut], summary="Получить вопросы по дисциплине")
def get_questions_by_discipline(discipline_id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id_discipline == discipline_id).first()
    
    if not discipline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {discipline_id} не найдена."
        )
    questions = db.query(Question).filter(Question.id_discipline == discipline_id).all()
    return questions

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить вопрос по ID")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id_question == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопрос с ID {question_id} не найден."
        )

    try:
        db.delete(question)
        db.commit()

        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении вопроса из базы данных."
        )
    
@router.patch("/{question_id}", response_model=QuestionOut, summary="Частично изменить вопрос")
def patch_question(question_id: int, updated_data: QuestionPatch, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id_question == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопрос с ID {question_id} не найден."
        )

    # Проверка диапазона для complexity_score, если значение передано, проверяем его
    if updated_data.complexity_score is not None:
        if not (0.1 <= updated_data.complexity_score <= 1.0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недопустимое значение сложности: {updated_data.complexity_score}. Должно быть от 0.1 до 1.0."
            )

    # Проверка дисциплины (если меняется)
    if updated_data.id_discipline is not None:
        discipline = db.query(Discipline).filter(Discipline.id_discipline == updated_data.id_discipline).first()
        if not discipline:
            raise HTTPException(status_code=404, detail="Дисциплина не найдена.")

    # Проверка на дубликат (если меняется контент или дисциплина)
    if updated_data.question_content or updated_data.id_discipline:
        check_content = updated_data.question_content or question.question_content
        check_discipline = updated_data.id_discipline or question.id_discipline
        
        duplicate = db.query(Question).filter(
            Question.id_discipline == check_discipline,
            Question.question_content == check_content,
            Question.id_question != question_id
        ).first()

        if duplicate:
            raise HTTPException(status_code=400, detail="Такой вопрос уже существует.")

    update_dict = updated_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(question, key, value)

    try:
        db.commit()
        db.refresh(question)
        return question
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении в базу.")