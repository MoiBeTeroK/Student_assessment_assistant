from sqlalchemy import Column, Integer, String
from Backend.database import Base

class Discipline(Base):
    __tablename__ = "disciplines"
    id_discipline = Column(Integer, primary_key=True, index=True)
    name_discipline = Column(String(255), nullable=False)