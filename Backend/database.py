# from sqlalchemy import Column, Integer, String, create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# # настройка подключения
# DATABASE_URL = "postgresql://postgres:123@localhost:5432/diplom_db"

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # модели(таблицы)
# class Discipline(Base):
#     __tablename__ = "disciplines"

#     id_discipline = Column(Integer, primary_key=True, index=True)
#     name_discipline = Column(String(255), nullable=False)

# # функция про запас
# def init_db():
#     Base.metadata.create_all(bind=engine)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:123@localhost:5432/diplom_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # Все остальные модели будут наследоваться от него