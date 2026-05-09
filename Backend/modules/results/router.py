from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database import get_db
# from dependencies import scorer

from . import models, schemas

from modules.students.models import Student
from modules.questions.models import Question
from modules.tests.models import Test
from modules.storage.models import Audio

router = APIRouter(
    prefix="/results",
    tags=["Results"]
)

@router.post("/calculate", response_model=schemas.CalculationResponse, summary="Рассчитать предварительную оценку")
def calculate_results(data: schemas.CalculateExamRequest, db: Session = Depends(get_db)):
    result_entry = db.query(models.ExamResult).filter(models.ExamResult.id_result == data.id_result).first()
    if not result_entry:
        raise HTTPException(status_code=404, detail="Запись результата не найдена")

    rows_for_scorer = []
    
    for audio_id in data.audio_ids:
        audio_entry = db.query(Audio).filter(Audio.id_audio == audio_id).first()
        
        if not audio_entry:
            raise HTTPException(status_code=404, detail=f"Аудио {audio_id} не найдено")
            
        question_data = audio_entry.question
        
        rows_for_scorer.append({
            "id_audio": audio_entry.id_audio,
            "question": question_data.question_content,
            "reference": question_data.standard_answer,
            "student": audio_entry.transcript,
        })

    model_results = scorer.score_batch(rows_for_scorer)
    
    final_analytics = []
    total_grade = 0
    
    for i, res in enumerate(model_results):
        analysis_item = {
            "id_audio": rows_for_scorer[i]["id_audio"],
            "similarity": res["S"],
            "term_coverage": res["C_raw"],
            "speech_coherence": res["H"],
            "question_rec_grade": res["grade"],
            "comment": f"Сходство: {res['S']:.2f}. Анализ Rubert."
        }
        final_analytics.append(analysis_item)
        total_grade += res["grade"]
        
    count = len(model_results)
    rec_grade = int(round(total_grade / count)) if count > 0 else 0

    result_entry.rec_grade = rec_grade
    result_entry.analitics_data = final_analytics
    
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении расчетов")

    return {
        "rec_grade": rec_grade,
        "analitics_data": final_analytics
    }

@router.post("/", response_model=schemas.ExamResultOut, status_code=status.HTTP_201_CREATED, summary="Сохранить результат экзамена")
def create_exam_result(result_data: schemas.ExamResultAll, db: Session = Depends(get_db)):
    if not db.query(Student).filter(Student.id_student == result_data.id_student).first():
        raise HTTPException(status_code=404, detail="Студент не найден")

    if not db.query(Test).filter(Test.id_test == result_data.id_test).first():
        raise HTTPException(status_code=404, detail="Тест не найден")

    new_result = models.ExamResult(**result_data.model_dump())
    
    try:
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        return new_result
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении результата")

@router.get("/student/{student_id}", response_model=List[schemas.ExamResultOut], summary="Получить результаты студента")
def get_student_results(student_id: int, db: Session = Depends(get_db)):
    if not db.query(Student).filter(Student.id_student == student_id).first():
        raise HTTPException(status_code=404, detail="Студент не найден")
        
    results = db.query(models.ExamResult).filter(models.ExamResult.id_student == student_id).all()
    if not results:
        raise HTTPException(status_code=404, detail="Результаты не найдены")
        
    return results

@router.get("/{result_id}", response_model=schemas.ExamResultOut, summary="Получить конкретный результат по ID")
def get_result_by_id(result_id: int, db: Session = Depends(get_db)):
    result = db.query(models.ExamResult).filter(models.ExamResult.id_result == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Результат не найден")
    return result

@router.post("/start", response_model=schemas.ExamStartResponse, status_code=status.HTTP_201_CREATED, summary="Начать экзамен")
def start_exam(data: schemas.ExamResultCreate, db: Session = Depends(get_db)):
    if not db.query(Student).filter(Student.id_student == data.id_student).first():
        raise HTTPException(status_code=404, detail="Студент не найден")

    if not db.query(Test).filter(Test.id_test == data.id_test).first():
        raise HTTPException(status_code=404, detail="Тест не найден")

    new_result = models.ExamResult(
        id_student=data.id_student,
        id_test=data.id_test,
        date=datetime.now(),
        rec_grade=None,
        final_grade=None,
        analitics_data=None
    )
    
    try:
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        return new_result
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при инициализации экзамена")
    
@router.put("/{id_result}/final-grade", response_model=schemas.ExamResultOut, summary="Установить финальную оценку")
def set_final_grade(id_result: int, data: schemas.FinalGradePut, db: Session = Depends(get_db)):
    result = db.query(models.ExamResult).filter(models.ExamResult.id_result == id_result).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Результат не найден")

    result.final_grade = data.final_grade
    
    try:
        db.commit()
        db.refresh(result)
        return result
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении данных")