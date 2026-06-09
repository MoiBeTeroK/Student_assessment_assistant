from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from . import schemas, service
from modules.questions.models import Question
from modules.disciplines.models import Discipline
from modules.results.models import ExamResult
from modules.storage.models import Audio


router = APIRouter(prefix="/gigachat", tags=["GigaChat"])


@router.post("/generate-answer", response_model=schemas.TextResponse, summary="Сгенерировать эталонный ответ")
async def generate_answer(data: schemas.GenerateAnswerRequest, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id_question == data.id_question).first()
    if not question:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Вопрос не найден")

    discipline = db.query(Discipline).filter(Discipline.id_discipline == question.id_discipline).first()
    discipline_name = discipline.name_discipline if discipline else "неизвестная дисциплина"

    text = await service.generate_standard_answer(question.question_content, discipline_name)
    return {"text": text}


@router.post("/generate-answer-by-text", response_model=schemas.TextResponse, summary="Сгенерировать эталонный ответ по тексту вопроса")
async def generate_answer_by_text(data: schemas.GenerateAnswerByTextRequest, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id_discipline == data.id_discipline).first()
    discipline_name = discipline.name_discipline if discipline else "неизвестная дисциплина"

    text = await service.generate_standard_answer(data.question_content, discipline_name)
    return {"text": text}


@router.post("/generate-comment", response_model=schemas.TextResponse, summary="Сгенерировать комментарий к ответу студента")
async def generate_comment(data: schemas.GenerateCommentRequest, db: Session = Depends(get_db)):
    result = db.query(ExamResult).filter(ExamResult.id_result == data.id_result).first()
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Результат не найден")

    audios = db.query(Audio).filter(Audio.id_result == data.id_result).all()
    if not audios:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нет аудиозаписей для данного результата")

    questions_data = []
    for audio in audios:
        q = db.query(Question).filter(Question.id_question == audio.id_question).first()
        if not q:
            continue
        questions_data.append({
            "question":        q.question_content,
            "standard_answer": q.standard_answer or "Эталонный ответ не задан",
            "transcript":      audio.transcript or "",
        })

    if not questions_data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Не удалось собрать данные для комментария")

    text = await service.generate_comment(questions_data, result.rec_grade or 0)
    return {"text": text}
