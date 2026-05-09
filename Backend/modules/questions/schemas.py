from pydantic import BaseModel, Field
from typing import Optional

class QuestionPartial(BaseModel):
    id_discipline: Optional[int] = None
    standard_answer: Optional[str] = None
    question_content: Optional[str] = None
    complexity_score: Optional[float] = None

class QuestionPatch(QuestionPartial):
    pass

class QuestionBase(QuestionPartial):
    id_discipline: int
    question_content: str

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id_question: int

    class Config:
        from_attributes = True
        
class QuestionImportSchema(QuestionBase):
    id_question: Optional[int] = None