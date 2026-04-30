from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from Backend.database import get_db
from Backend.modules.results.models import ExamResult
from Backend.modules.results.schemas import (
    ExamResultCreate, ExamResultOut, 
    CalculateExamRequest, CalculationResponse
)
from Backend.modules.students.models import Student
from Backend.modules.questions.models import Question
from Backend.modules.tests.models import Test, test_questions

from Backend.dependencies import scorer

router = APIRouter(
    prefix="/results",
    tags=["Results"]
)

@router.post("/calculate", response_model=CalculationResponse, summary="Рассчитать предварительную оценку")
def calculate_results(data: CalculateExamRequest, db: Session = Depends(get_db)):
    rows_for_scorer = []
    
    for ans in data.answers:
        question_data = (
            db.query(Question)
            .join(test_questions, Question.id_question == test_questions.c.id_question)
            .filter(test_questions.c.id_test == data.id_test)
            .filter(Question.id_question == ans.id_question)
            .first()
        )
        
        if not question_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Вопрос {ans.id_question} не привязан к тесту {data.id_test}"
            )
            
        rows_for_scorer.append({
            "id_question": question_data.id_question,
            "question": question_data.question_content,
            "reference": question_data.standard_answer,
            "student": ans.answer_text,
            "type": "основной" # По умолчанию
        })

    if not rows_for_scorer:
        raise HTTPException(status_code=400, detail="Список ответов пуст")

    # Вызов нейронки
    model_results = scorer.score_batch(rows_for_scorer)
    
    final_analytics = []
    total_score = 0
    total_grade = 0
    
    for i, res in enumerate(model_results):
        analysis_item = {
            "id_question": rows_for_scorer[i]["id_question"],
            "type": rows_for_scorer[i]["type"],
            "answer_st": rows_for_scorer[i]["student"],
            "similarity": res["S"],
            "term_coverage": res["C_raw"],
            "speech_coherence": res["H"],
            "question_rec_grade": res["grade"],
            "comment": f"Сходство: {res['S']:.2f}. Анализ выполнен моделью Rubert."
        }
        final_analytics.append(analysis_item)
        total_grade += res["grade"]
        
    count = len(model_results)
    rec_grade = int(round(total_grade / count)) 

    return {
        "rec_grade": rec_grade,
        "analitics_data": final_analytics
    }

@router.post("/", response_model=ExamResultOut, status_code=status.HTTP_201_CREATED, summary="Сохранить результат экзамена")
def create_exam_result(result_data: ExamResultCreate, db: Session = Depends(get_db)):
    # 1. Проверяем, существует ли студент
    student = db.query(Student).filter(Student.id_student == result_data.id_student).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {result_data.id_student} не найден."
        )

    # Проверяем, существует ли тест
    test = db.query(Test).filter(Test.id_test == result_data.id_test).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тест с ID {result_data.id_test} не найден."
        )

    new_result = ExamResult(**result_data.model_dump())
    
    try:
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        return new_result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при сохранении результата в базу данных."
        )

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