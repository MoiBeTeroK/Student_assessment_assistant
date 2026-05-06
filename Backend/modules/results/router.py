from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database import get_db
from modules.results.models import ExamResult
from modules.results.schemas import (
    ExamResultCreate, ExamResultOut, 
    CalculateExamRequest, CalculationResponse, ExamResultAll, 
    FinalGradePut, ExamStartResponse
)
from modules.students.models import Student
from modules.questions.models import Question
from modules.tests.models import Test, test_questions
from modules.storage.models import Audio

from dependencies import scorer

router = APIRouter(
    prefix="/results",
    tags=["Results"]
)

@router.post("/calculate", response_model=CalculationResponse, summary="Рассчитать предварительную оценку")
def calculate_results(data: CalculateExamRequest, db: Session = Depends(get_db)):
    result_entry = db.query(ExamResult).filter(ExamResult.id_result == data.id_result).first()
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
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при сохранении расчетов")

    return {
        "rec_grade": rec_grade,
        "analitics_data": final_analytics
    }

# @router.post("/", response_model=ExamResultOut, status_code=status.HTTP_201_CREATED, summary="Сохранить результат экзамена (после расчета)")
# def create_exam_result(result_data: ExamResultAll, db: Session = Depends(get_db)):
#     # Проверяем, существует ли студент
#     student = db.query(Student).filter(Student.id_student == result_data.id_student).first()
#     if not student:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Студент с ID {result_data.id_student} не найден."
#         )

#     # Проверяем, существует ли тест
#     test = db.query(Test).filter(Test.id_test == result_data.id_test).first()
#     if not test:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Тест с ID {result_data.id_test} не найден."
#         )

#     new_result = ExamResult(**result_data.model_dump())
    
#     try:
#         db.add(new_result)
#         db.commit()
#         db.refresh(new_result)
#         return new_result
        
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Ошибка при сохранении результата в базу данных."
#         )

@router.get("/student/{student_id}", response_model=List[ExamResultOut], summary="Получить все результаты студента")
def get_student_results(student_id: int, db: Session = Depends(get_db)):
    student_exists = db.query(Student).filter(Student.id_student == student_id).first()
    if not student_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден"
        )
        
    results = db.query(ExamResult).filter(ExamResult.id_student == student_id).all()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"У студента с ID {student_id} пока нет сохраненных результатов"
        )
        
    return results

@router.get("/{result_id}", response_model=ExamResultOut, summary="Получить конкретный результат по ID")
def get_result_by_id(result_id: int, db: Session = Depends(get_db)):
    result = db.query(ExamResult).filter(ExamResult.id_result == result_id).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Результат с ID {result_id} не найден"
        )
    return result

@router.post("/start", response_model=ExamStartResponse, status_code=status.HTTP_201_CREATED, summary="Инициализировать начало экзамена")
def start_exam(data: ExamResultCreate, db: Session = Depends(get_db)):
    # Проверяем существование студента
    student = db.query(Student).filter(Student.id_student == data.id_student).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Студент с ID {data.id_student} не найден"
        )

    # Проверяем существование теста
    test = db.query(Test).filter(Test.id_test == data.id_test).first()
    if not test:
        raise HTTPException(
            status_code=404,
            detail=f"Тест с ID {data.id_test} не найден"
        )

    new_result = ExamResult(
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
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ошибка при инициализации результата экзамена"
        )
    
@router.put("/{id_result}/final-grade", response_model=ExamResultOut, summary="Установить финальную оценку")
def set_final_grade(id_result: int, data: FinalGradePut, db: Session = Depends(get_db)):
    result = db.query(ExamResult).filter(ExamResult.id_result == id_result).first()
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Результат не найден"
        )

    result.final_grade = data.final_grade
    
    try:
        db.commit()
        db.refresh(result)
        return result
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ошибка при сохранении данных"
        )