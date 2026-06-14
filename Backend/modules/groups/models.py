from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Group(Base):
    __tablename__ = "groups"

    id_group = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(20), unique=True, nullable=False, index=True)

    is_archive = Column(Boolean, default=False, nullable=False)

    students = relationship("modules.students.models.Student", back_populates="group_rel", cascade="all, delete-orphan")
