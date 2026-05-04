from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuestionAnalysis(BaseModel):
    id_audio: int
    similarity: float
    term_coverage: float
    speech_coherence: float
    question_rec_grade: int
    comment: Optional[str] = None

class ExamResultBase(BaseModel):
    id_student: int
    id_test: int
    rec_grade: Optional[float] = None
    final_grade: Optional[float] = None
    date: datetime
    analitics_data: Optional[List[QuestionAnalysis]] = None

class ExamResultAll(BaseModel):
    id_result: int
    final_grade: Optional[float] = None
    analitics_data: Optional[List[QuestionAnalysis]] = None

class ExamResultCreate(BaseModel):
    id_student: int
    id_test: int

class ExamResultOut(ExamResultBase):
    id_result: int

    class Config:
        from_attributes = True

class StudentAudioInput(BaseModel):
    id_audio: int

class CalculateExamRequest(BaseModel):
    id_test: int
    id_result: int
    audio_ids: List[int] 

class CalculationResponse(BaseModel):
    rec_grade: int
    analitics_data: List[QuestionAnalysis]

class FinalGradePut(BaseModel):
    final_grade: float