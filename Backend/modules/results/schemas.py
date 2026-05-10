from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime
from modules.storage.schemas import AudioBase

class AudioWithText(AudioBase):
    question_text: str

class QuestionAnalysis(BaseModel):
    audio: AudioWithText
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
    id_student: int
    id_test: int
    final_grade: Optional[float] = None
    analitics_data: Optional[List[QuestionAnalysis]] = None

class ExamResultCreate(BaseModel):
    id_student: int
    id_test: int

class ExamStartResponse(BaseModel):
    id_result: int
    id_student: int
    id_test: int
    date: datetime
    
class ExamResultOut(ExamResultBase):
    id_result: int
    model_config = ConfigDict(from_attributes=True)

class CalculateExamRequest(BaseModel):
    id_result: int

class CalculationResponse(BaseModel):
    rec_grade: int
    analitics_data: List[QuestionAnalysis]

class FinalGradePut(BaseModel):
    final_grade: float

class MetricAverages(BaseModel):
    avg_similarity: float
    avg_term_coverage: float
    avg_speech_coherence: float

class GradeDistribution(BaseModel):
    ai_grades: Dict[int, int]
    final_grades: Dict[int, int]

class WorstQuestion(BaseModel):
    id: int
    question_text: str
    avg_similarity: float

class GroupAnalyticsOut(BaseModel):
    group_id: int
    discipline_id: int
    total_exams: int
    ai_agreement_rate: float
    avg_grade_difference: float
    metrics: MetricAverages
    worst_question: Optional[WorstQuestion] = None
    distribution: GradeDistribution