from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from Backend.database import Base

class Discipline(Base):
    __tablename__ = "disciplines"
    id_discipline = Column(Integer, primary_key=True, index=True)
    name_discipline = Column(String(255), nullable=False)

    tests = relationship("Backend.modules.tests.models.Test", back_populates="discipline")