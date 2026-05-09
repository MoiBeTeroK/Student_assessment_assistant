from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Student(Base):
    __tablename__ = "students"

    id_student = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    id_group = Column(Integer, ForeignKey("groups.id_group"), nullable=False)

    group_rel = relationship("modules.groups.models.Group", back_populates="students")
    exam_results = relationship("modules.results.models.ExamResult", back_populates="student")