from pydantic import BaseModel

class QuestionBase(BaseModel):
    id_discipline: int
    standard_answer: str
    question_content: str

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    id_discipline: int
    standard_answer: str
    question_content: str
    
class QuestionOut(QuestionBase):
    id_question: int

    class Config:
        from_attributes = True