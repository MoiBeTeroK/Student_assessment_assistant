from pydantic import BaseModel
from typing import Optional

class AudioBase(BaseModel):
    id_audio: int
    id_question: int
    id_result: int
    filename: str
    transcript: Optional[str] = None

class AudioCreate(AudioBase):
    pass

class AudioUploadResponse(BaseModel):
    url: str
    filename: str
    id_audio: Optional[int] = None

    class Config:
        from_attributes = True

class AudioFullResponse(AudioBase):
    id_audio: int

    class Config:
        from_attributes = True