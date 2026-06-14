from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from database import Base

test_questions = Table(
    "test_questions",
    Base.metadata,
    Column("id_test", Integer, ForeignKey("tests.id_test"), primary_key=True),
    Column("id_question", Integer, ForeignKey("questions.id_question"), primary_key=True)
)

class Test(Base):
    __tablename__ = "tests"
    id_test = Column(Integer, primary_key=True, index=True)
    test_number = Column(Integer, nullable=False)
    is_archive = Column(Boolean, default=False, nullable=False)
    
    # FK указывает на имя таблицы 'disciplines' и колонку 'id_discipline'
    id_discipline = Column(Integer, ForeignKey("disciplines.id_discipline", ondelete="CASCADE"), nullable=False)

    # Связь для удобства доставать объект дисциплины из билета
    discipline = relationship("modules.disciplines.models.Discipline", back_populates="tests")

    __table_args__ = (
        UniqueConstraint('id_discipline', 'test_number', name='_discipline_test_uc'),
    )

    questions = relationship("modules.questions.models.Question", secondary=test_questions, backref="tests")
    exam_results = relationship("modules.results.models.ExamResult", back_populates="test")