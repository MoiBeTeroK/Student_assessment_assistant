from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Audio(Base):
    __tablename__ = "audio"

    id_audio = Column(Integer, primary_key=True, index=True, autoincrement=True)

    id_question = Column(Integer, ForeignKey("questions.id_question"), nullable=False)
    id_result = Column(Integer, ForeignKey("exam_results.id_result"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    transcript = Column(Text, nullable=False)

    question = relationship("modules.questions.models.Question", back_populates="audios")
    exam_result = relationship("modules.results.models.ExamResult", back_populates="audios")