from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from modules.questions.models import Question
from modules.disciplines.models import Discipline
from modules.questions.schemas import QuestionCreate, QuestionOut, QuestionUpdate

router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)

@router.post("/", response_model=QuestionOut, status_code=status.HTTP_201_CREATED, summary="Создать новый вопрос")
def create_question(question_data: QuestionCreate, db: Session = Depends(get_db)):
    # 1. Проверяем, существует ли дисциплина, к которой привязываем вопрос
    discipline = db.query(Discipline).filter(
        Discipline.id_discipline == question_data.id_discipline
    ).first()
    
    if not discipline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дисциплина с ID {question_data.id_discipline} не найдена. Невозможно создать вопрос."
        )

    # 2. ПРОВЕРКА НА ДУБЛИКАТ
    # Ищем, нет ли уже такого же вопроса в этой дисциплине
    existing_question = db.query(Question).filter(
        Question.id_discipline == question_data.id_discipline,
        Question.question_content == question_data.question_content
    ).first()

    if existing_question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой вопрос уже существует в данной дисциплине."
        )

    # 3. Создаем экземпляр модели Question
    new_question = Question(**question_data.model_dump())
    
    try:
        # Добавляем в сессию и фиксируем изменения
        db.add(new_question)
        db.commit()
        
        # Обновляем объект, чтобы получить сгенерированный базой id_question
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
    # Проверяем, существует ли дисциплина вообще
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
    """
    Удаляет вопрос из базы данных по его уникальному ID.
    """
    
    # 1. Ищем вопрос в базе
    question = db.query(Question).filter(Question.id_question == question_id).first()
    
    # 2. Если вопрос не найден — кидаем 404
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопрос с ID {question_id} не найден."
        )

    try:
        # 3. Удаляем и фиксируем
        db.delete(question)
        db.commit()
        
        # Для DELETE с кодом 204 возвращать тело ответа не нужно
        return None
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении вопроса из базы данных."
        )
    
@router.put("/{question_id}", response_model=QuestionOut, summary="Изменить вопрос и ответ")
def update_question(question_id: int, updated_data: QuestionUpdate, db: Session = Depends(get_db)):
    # 1. Ищем существующий вопрос
    question = db.query(Question).filter(Question.id_question == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопрос с ID {question_id} не найден."
        )

    # 2. Проверяем, существует ли новая дисциплина (если её меняют)
    discipline = db.query(Discipline).filter(Discipline.id_discipline == updated_data.id_discipline).first()
    if not discipline:
        raise HTTPException(
            status_code=404, 
            detail=f"Дисциплина с ID {updated_data.id_discipline} не найдена."
        )

    # 3. Проверка на дубликат (чтобы не изменить вопрос на такой, который уже есть)
    duplicate = db.query(Question).filter(
        Question.id_discipline == updated_data.id_discipline,
        Question.question_content == updated_data.question_content,
        Question.id_question != question_id  # Исключаем сам редактируемый вопрос
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Такой вопрос уже существует в этой дисциплине."
        )

    # 4. Обновляем поля
    # model_dump() вытащит все данные из схемы в виде словаря
    update_dict = updated_data.model_dump()
    for key, value in update_dict.items():
        setattr(question, key, value)

    try:
        db.commit()
        db.refresh(question)
        return question
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ошибка при обновлении данных в базе."
        )