from pydantic import BaseModel, Field
from typing import Optional

class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    group: str = Field(..., min_length=1, max_length=10)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    # Мы явно указываем Optional и значение по умолчанию None
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    group: Optional[str] = Field(None, min_length=1, max_length=10)

class StudentOut(StudentBase):
    id_student: int

    class Config:
        from_attributes = True