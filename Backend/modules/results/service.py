from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime
from typing import List

from dependencies import get_scorer
from . import models, schemas, analytics

from modules.students.models import Student
from modules.tests.models import Test
from modules.storage.models import Audio

def calculate_results(db: Session, data: schemas.CalculateExamRequest) -> dict:
    result_entry = db.query(models.ExamResult).filter(models.ExamResult.id_result == data.id_result).first()
    if not result_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись результата не найдена")

    audio_records = db.query(Audio).filter(Audio.id_result == data.id_result).all()
    if not audio_records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Для данного результата не найдено аудиозаписей")

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

    scorer = get_scorer()
    model_results = scorer.score_batch(rows_for_scorer)
    
    db_analytics = []
    total_grade = 0
    
    for i, res in enumerate(model_results):
        audio_rec = audio_records[i] 
        
        analysis_item = {
            "id_audio": audio_rec.id_audio,
            "similarity": res["S"],
            "term_coverage": res["C_raw"],
            "speech_coherence": res["H"],
            "question_rec_grade": res["grade"],
            "comment": ""
        }
        db_analytics.append(analysis_item)
        total_grade += res["grade"]
        
    count = len(model_results)
    rec_grade = int(round(total_grade / count)) if count > 0 else 0

    result_entry.rec_grade = rec_grade
    result_entry.analitics_data = db_analytics
    
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при сохранении расчетов")

    response_analytics = []
    for i, res in enumerate(model_results):
        audio_rec = audio_records[i]
        response_analytics.append({
            "audio": {
                "id_audio": audio_rec.id_audio,
                "id_question": audio_rec.id_question,
                "id_result": audio_rec.id_result,
                "filename": audio_rec.filename,
                "transcript": audio_rec.transcript,
                "question_text": audio_rec.question.question_content if audio_rec.question else ""
            },
            "similarity": res["S"],
            "term_coverage": res["C_raw"],
            "speech_coherence": res["H"],
            "question_rec_grade": res["grade"],
            "comment": ""
        })

    return {
        "rec_grade": rec_grade,
        "analitics_data": response_analytics
    }

def _enrich_analytics_data(db: Session, result: models.ExamResult) -> models.ExamResult:
    if result.analitics_data and isinstance(result.analitics_data, list):
        validated_analytics = []
        
        for item in result.analitics_data:
            if isinstance(item, dict):
                id_audio = item["audio"].get("id_audio") if "audio" in item else item.get("id_audio")
                
                audio_rec = db.query(Audio).filter(Audio.id_audio == id_audio).first()
                if audio_rec:
                    audio_schema = schemas.AudioWithText(
                        id_audio=audio_rec.id_audio,
                        id_question=audio_rec.id_question,
                        id_result=audio_rec.id_result,
                        filename=audio_rec.filename,
                        transcript=audio_rec.transcript or "",
                        question_text=audio_rec.question.question_content if audio_rec.question else ""
                    )

                    analysis_schema = schemas.QuestionAnalysis(
                        audio=audio_schema,
                        similarity=item.get("similarity", 0.0),
                        term_coverage=item.get("term_coverage", 0.0),
                        speech_coherence=item.get("speech_coherence", 0.0),
                        question_rec_grade=item.get("question_rec_grade", 0),
                        comment=item.get("comment", "")
                    )
                    validated_analytics.append(analysis_schema)
                    
        result.analitics_data = validated_analytics
        
    return result


def get_student_results(db: Session, student_id: int) -> List[models.ExamResult]:
    if not db.query(Student).filter(Student.id_student == student_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден")
        
    results = db.query(models.ExamResult).filter(models.ExamResult.id_student == student_id).all()
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Результаты не найдены")
        
    for result in results:
        _enrich_analytics_data(db, result)
        
    return results


def get_result_by_id(db: Session, result_id: int) -> models.ExamResult:
    result = db.query(models.ExamResult).filter(models.ExamResult.id_result == result_id).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Результат не найден")
    return _enrich_analytics_data(db, result)

def start_exam(db: Session, data: schemas.ExamResultCreate) -> models.ExamResult:
    if not db.query(Student).filter(Student.id_student == data.id_student).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Студент не найден")

    if not db.query(Test).filter(Test.id_test == data.id_test).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при инициализации экзамена")

def set_final_grade(db: Session, id_result: int, data: schemas.FinalGradePut) -> models.ExamResult:
    result = db.query(models.ExamResult).filter(models.ExamResult.id_result == id_result).first()
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Результат не найден")

    result.final_grade = data.final_grade
    
    try:
        db.commit()
        db.refresh(result)
        return _enrich_analytics_data(db, result)
        
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при сохранении данных")
    
def get_group_analytics(db: Session, group_id: int, discipline_id: int) -> dict:
    results = db.query(models.ExamResult).join(Student).join(Test).filter(
        Student.id_group == group_id,
        Test.id_discipline == discipline_id,
        models.ExamResult.final_grade != None
    ).all()

    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данные для анализа не найдены")

    stats = analytics.calculate_group_statistics(results)
    
    return {
        "group_id": group_id,
        "discipline_id": discipline_id,
        **stats
    }
def get_results_by_discipline_and_year(db: Session, discipline_id: int, year: int) -> List[models.ExamResult]:
    results = db.query(models.ExamResult).join(Test).filter(
        Test.id_discipline == discipline_id,
        extract('year', models.ExamResult.date) == year
    ).all()

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Результаты экзаменов для указанной дисциплины и года не найдены"
        )
        
    for result in results:
        if result.analitics_data and isinstance(result.analitics_data, list):
            validated_analytics = []
            
            for item in result.analitics_data:
                if isinstance(item, dict):
                    id_audio = item["audio"].get("id_audio") if "audio" in item else item.get("id_audio")
                    
                    audio_rec = db.query(Audio).filter(Audio.id_audio == id_audio).first()
                    audio_schema = schemas.AudioWithText(
                        id_audio=audio_rec.id_audio,
                        id_question=audio_rec.id_question,
                        id_result=audio_rec.id_result,
                        filename=audio_rec.filename,
                        transcript=audio_rec.transcript or "",
                        question_text=audio_rec.question.question_content if audio_rec.question else ""
                    )

                    analysis_schema = schemas.QuestionAnalysis(
                        audio=audio_schema,
                        similarity=item.get("similarity", 0.0),
                        term_coverage=item.get("term_coverage", 0.0),
                        speech_coherence=item.get("speech_coherence", 0.0),
                        question_rec_grade=item.get("question_rec_grade", 0),
                        comment=item.get("comment", "")
                    )
                    
                    validated_analytics.append(analysis_schema)
            result.analitics_data = validated_analytics
        
    return results