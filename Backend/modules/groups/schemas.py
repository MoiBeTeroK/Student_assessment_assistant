from pydantic import BaseModel, Field
from typing import Optional

class GroupBase(BaseModel):
    group_name: str = Field(..., min_length=2, max_length=20, example="ПМ43")
    is_archive: Optional[bool] = False

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    group_name: Optional[str] = Field(None, min_length=2, max_length=20)
    is_archive: Optional[bool] = None

class GroupArchiveUpdate(BaseModel):
    is_archive: bool = Field(..., description="Новый статус архивности группы")
    
class GroupOut(GroupBase):
    id_group: int
    is_archive: bool

    class Config:
        from_attributes = True