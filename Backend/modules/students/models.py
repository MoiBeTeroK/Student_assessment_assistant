from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from Backend.database import Base

class Student(Base):
    __tablename__ = "students"

    id_student = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    group = Column(String(10), nullable=False)

    exam_results = relationship("Backend.modules.results.models.ExamResult", back_populates="student")