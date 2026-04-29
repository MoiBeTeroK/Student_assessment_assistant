from sqlalchemy import Column, Integer, Numeric, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from Backend.database import Base

class ExamResult(Base):
    __tablename__ = "exam_results"

    id_result = Column(Integer, primary_key=True, index=True)
    id_student = Column(Integer, ForeignKey("students.id_student"), nullable=False)
    id_test = Column(Integer, ForeignKey("tests.id_test"), nullable=False)
    
    rec_grade = Column(Numeric(3, 2))
    final_grade = Column(Numeric(3, 2))
    
    # Автоматическая установка времени начала
    date_start = Column(TIMESTAMP, server_default=func.now())
    date_end = Column(TIMESTAMP)
    
    analitics_data = Column(JSONB)

    student = relationship("Backend.modules.students.models.Student", back_populates="exam_results")
    test = relationship("Backend.modules.tests.models.Test", back_populates="exam_results")