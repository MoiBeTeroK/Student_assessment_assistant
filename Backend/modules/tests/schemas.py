from pydantic import BaseModel
from typing import List, Optional

class TestBase(BaseModel):
    test_number: int
    id_discipline: int

class TestCreate(TestBase):
    question_ids: List[int] = []

class TestUpdate(BaseModel):
    test_number: Optional[int] = None
    id_discipline: Optional[int] = None
    question_ids: Optional[List[int]] = None
    
class QuestionShortOut(BaseModel):
    id_question: int
    question_content: str 
    standard_answer: Optional[str] = None
    complexity_score: Optional[float] = None

    class Config:
        from_attributes = True

class TestIdOnly(BaseModel):
    id_test: int

    class Config:
        from_attributes = True

class TestOut(BaseModel):
    id_test: int
    test_number: int
    id_discipline: int
    questions: List[QuestionShortOut] = [] 

    class Config:
        from_attributes = True

class TestGenerateRequest(BaseModel):
    id_discipline: int
    num_tests: int
    questions_per_test: int