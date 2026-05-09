from pydantic import BaseModel

class DisciplineBase(BaseModel):
    name_discipline: str

class DisciplineCreate(DisciplineBase):
    pass

class DisciplineOut(DisciplineBase):
    id_discipline: int

    class Config:
        from_attributes = True