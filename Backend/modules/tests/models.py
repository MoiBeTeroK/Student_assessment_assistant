from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from Backend.database import Base

class Test(Base):
    __tablename__ = "tests"
    id_test = Column(Integer, primary_key=True, index=True)
    test_number = Column(Integer, nullable=False)
    
    # FK указывает на имя таблицы 'disciplines' и колонку 'id_discipline'
    id_discipline = Column(Integer, ForeignKey("disciplines.id_discipline", ondelete="CASCADE"), nullable=False)

    # Связь для удобства доставать объект дисциплины из билета
    discipline = relationship("Backend.modules.disciplines.models.Discipline", back_populates="tests")

    __table_args__ = (
        UniqueConstraint('id_discipline', 'test_number', name='_discipline_test_uc'),
    )