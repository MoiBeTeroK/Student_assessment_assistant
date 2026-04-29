from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuestionAnalysis(BaseModel):
    id_question: int
    type: str
    question_content: str
    answer: str
    similarity: float
    comment: str

class ExamResultBase(BaseModel):
    id_student: int
    id_test: int
    rec_grade: Optional[float] = None
    final_grade: Optional[float] = None
    date: datetime
    analitics_data: Optional[List[QuestionAnalysis]] = None

class ExamResultCreate(ExamResultBase):
    # Теперь дата обязательна при создании
    pass

class ExamResultOut(ExamResultBase):
    id_result: int

    class Config:
        from_attributes = True