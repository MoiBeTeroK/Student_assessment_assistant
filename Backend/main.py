from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.auth.router import router as auth_router
from modules.disciplines.router import router as disciplines_router
from modules.students.router import router as students_router
from modules.groups.router import router as groups_router
from modules.tests.router import router as tests_router
from modules.questions.router import router as questions_router
from modules.results.router import router as results_router
# from modules.storage.router import router as storage_router

# from speech_to_text.speech_to_text_main.speach_to_text_new import init_asr
# from speech_to_text.speech_to_text_main.config import MODEL_DIR
# from speech_to_text.speech_to_text_main.punctuation import init_punctuation

app = FastAPI(title="Student assessment assistant")

# @app.on_event("startup")
# async def load_stt_models():
#     print("Предзагрузка Speech-To-Text моделей...")
#     init_asr(str(MODEL_DIR))

#     print("Загружается модель пунктуации...")
#     init_punctuation()

#     print("Все модели успешно загружены")

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
app.include_router(auth_router)
app.include_router(disciplines_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(groups_router, prefix="/api")
app.include_router(tests_router, prefix="/api")
app.include_router(questions_router, prefix="/api")
app.include_router(results_router, prefix="/api")
# app.include_router(storage_router)
