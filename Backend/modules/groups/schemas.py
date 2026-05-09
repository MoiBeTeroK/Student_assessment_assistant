from pydantic import BaseModel, Field
from typing import Optional

class GroupBase(BaseModel):
    group_name: str = Field(..., min_length=2, max_length=20, example="ПМ43")

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    group_name: Optional[str] = Field(None, min_length=2, max_length=20)

class GroupOut(GroupBase):
    id_group: int

    class Config:
        from_attributes = True
