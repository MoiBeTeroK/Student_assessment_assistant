from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.disciplines.router import router as disciplines_router
from modules.students.router import router as students_router
from modules.tests.router import router as tests_router
from modules.questions.router import router as questions_router
from modules.results.router import router as results_router
from modules.storage.router import router as storage_router

app = FastAPI(title="Student assessment assistant")

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # Разрешаем запросы с указанных адресов
    allow_credentials=True,            # Разрешаем куки и авторизацию
    allow_methods=["*"],               # Разрешаем все методы
    allow_headers=["*"],               # Разрешаем все заголовки
)

# Подключаем роутеры
app.include_router(disciplines_router)
app.include_router(students_router)
app.include_router(tests_router)
app.include_router(questions_router)
app.include_router(results_router)
app.include_router(storage_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "online",
        "message": "Welcome to Student assessment assistant API"
    }