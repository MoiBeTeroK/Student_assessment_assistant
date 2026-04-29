from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Backend.modules.disciplines.router import router as disciplines_router
from Backend.modules.students.router import router as students_router
from Backend.modules.tests.router import router as tests_router
from Backend.modules.questions.router import router as questions_router

app = FastAPI(title="Student assessment assistant")

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # Разрешаем запросы с указанных адресов
    allow_credentials=True,            # Разрешаем куки и авторизацию
    allow_methods=["*"],               # Разрешаем все методы
    allow_headers=["*"],               # Разрешаем все заголовки
)

# Подключаем роутеры
app.include_router(disciplines_router, prefix="/disciplines", tags=["Disciplines"])
app.include_router(students_router, prefix="/students", tags=["Students"])
app.include_router(tests_router, prefix="/tests", tags=["Tests"])
app.include_router(questions_router, prefix="/questions", tags=["Questions"])

@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "online",
        "message": "Welcome to Student assessment assistant API"
    }