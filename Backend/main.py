from fastapi import FastAPI
from Backend.modules.disciplines.router import router as disciplines_router
from Backend.modules.students.router import router as students_router

app = FastAPI(title="Student assessment assistant")

# Подключаем роутер дисциплин
app.include_router(disciplines_router)

# Подключаем роутер студентов
app.include_router(students_router)