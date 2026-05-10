from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database import get_db
from dependencies import scorer

from . import models, schemas, analytics

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

    audio_records = db.query(Audio).filter(Audio.id_result == data.id_result).all()
    if not audio_records:
        raise HTTPException(status_code=404, detail="Для данного результата не найдено аудиозаписей")

    rows_for_scorer = []
    for audio_entry in audio_records:
        question_data = audio_entry.question
        if not question_data:
            continue
            
        rows_for_scorer.append({
            "id_audio": audio_entry.id_audio,
            "question": question_data.question_content or "", 
            "reference": question_data.standard_answer or "",
            "student": audio_entry.transcript or "",
        })

    model_results = scorer.score_batch(rows_for_scorer)
    
    final_analytics = []
    total_grade = 0
    
    for i, res in enumerate(model_results):
        audio_rec = audio_records[i] 
        
        analysis_item = {
            "audio": {
                "id_audio": audio_rec.id_audio,
                "id_question": audio_rec.id_question,
                "id_result": audio_rec.id_result,
                "filename": audio_rec.filename,
                "transcript": audio_rec.transcript,
                "question_text": audio_rec.question.question_content # Текст берем из связи
            },
            "similarity": res["S"],
            "term_coverage": res["C_raw"],
            "speech_coherence": res["H"],
            "question_rec_grade": res["grade"],
            "comment": ""
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
    
@router.get("/analytics/group/{group_id}/discipline/{discipline_id}", response_model=schemas.GroupAnalyticsOut)
def get_group_analytics(group_id: int, discipline_id: int, db: Session = Depends(get_db)):
    results = db.query(models.ExamResult).join(Student).join(Test).filter(
        Student.id_group == group_id,
        Test.id_discipline == discipline_id,
        models.ExamResult.final_grade != None
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail="Данные для анализа не найдены")

    stats = analytics.calculate_group_statistics(results)
    
    return {
        "group_id": group_id,
        "discipline_id": discipline_id,
        **stats
    }