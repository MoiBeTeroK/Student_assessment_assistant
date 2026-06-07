from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Discipline(Base):
    __tablename__ = "disciplines"
    id_discipline = Column(Integer, primary_key=True, index=True)
    name_discipline = Column(String(255), nullable=False)
    owner_id = Column(Integer, nullable=False, default=1)

    tests = relationship("modules.tests.models.Test", back_populates="discipline")
    questions = relationship("modules.questions.models.Question", back_populates="discipline")