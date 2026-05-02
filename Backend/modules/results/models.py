from sqlalchemy import Column, Integer, Numeric, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database import Base

class ExamResult(Base):
    __tablename__ = "exam_results"

    id_result = Column(Integer, primary_key=True, index=True)
    id_student = Column(Integer, ForeignKey("students.id_student"), nullable=False)
    id_test = Column(Integer, ForeignKey("tests.id_test"), nullable=False)
    
    rec_grade = Column(Numeric(3, 2))
    final_grade = Column(Numeric(3, 2))
    
    date = Column(TIMESTAMP)
    
    analitics_data = Column(JSONB)

    student = relationship("modules.students.models.Student", back_populates="exam_results")
    test = relationship("modules.tests.models.Test", back_populates="exam_results")