from pydantic import BaseModel
from typing import List
from datetime import datetime

class QuestionAnalysis(BaseModel):
    id_question: int
    type: str
    answer_st: str
    similarity: float
    term_coverage: float
    speech_coherence: float
    question_rec_grade: int
    comment: str

class ExamResultBase(BaseModel):
    id_student: int
    id_test: int
    rec_grade: float
    final_grade: float
    date: datetime
    analitics_data: List[QuestionAnalysis]

class ExamResultCreate(ExamResultBase):
    pass

class ExamResultOut(ExamResultBase):
    id_result: int

    class Config:
        from_attributes = True