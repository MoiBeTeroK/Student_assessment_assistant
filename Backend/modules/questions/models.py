from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Question(Base):
    __tablename__ = "questions"

    id_question = Column(Integer, primary_key=True, index=True)
    id_discipline = Column(Integer, ForeignKey("disciplines.id_discipline"), nullable=False)
    standard_answer = Column(String, nullable=False)
    question_content = Column(String, nullable=False)

    discipline = relationship("modules.disciplines.models.Discipline", back_populates="questions")
    audios = relationship("modules.storage.models.Audio", back_populates="question")