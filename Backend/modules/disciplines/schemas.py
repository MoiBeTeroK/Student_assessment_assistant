from pydantic import BaseModel

# Базовая схема: общие поля для всех действий
class DisciplineBase(BaseModel):
    name_discipline: str

# Схема для создания (что мы ждем от фронтенда)
class DisciplineCreate(DisciplineBase):
    pass

# Схема для ответа (что мы возвращаем пользователю, включая ID)
class DisciplineOut(DisciplineBase):
    id_discipline: int

    class Config:
        # Это позволяет Pydantic читать данные прямо из объектов SQLAlchemy
        from_attributes = True