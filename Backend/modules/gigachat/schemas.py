from pydantic import BaseModel


class GenerateAnswerRequest(BaseModel):
    id_question: int


class GenerateAnswerByTextRequest(BaseModel):
    question_content: str
    id_discipline: int


class GenerateCommentRequest(BaseModel):
    id_result: int


class TextResponse(BaseModel):
    text: str
