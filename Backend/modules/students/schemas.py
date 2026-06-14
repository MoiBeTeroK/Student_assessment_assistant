from pydantic import BaseModel, Field
from typing import List, Optional
from modules.groups.schemas import GroupOut, GroupBase

class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, example="Иванов Иван Иванович")

class StudentCreate(StudentBase):
    id_group: int

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    id_group: Optional[int] = Field(None)
    is_archive: Optional[bool] = Field(None)

# Вывод данных (для GET ручек)
class StudentOut(StudentBase):
    id_student: int
    is_archive: bool
    group: GroupOut = Field(..., alias="group_rel")

    class Config:
        from_attributes = True
        populate_by_name = True

# Импорт данных
class StudentImportSchema(BaseModel):
    id_student: Optional[int] = None
    name: str
    group: GroupBase 

class ImportResponse(BaseModel):
    students: List[StudentOut]