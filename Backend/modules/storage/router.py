from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from . import schemas, service

router = APIRouter(prefix="/storage", tags=["Storage"])

@router.post("/upload-audio", response_model=schemas.AudioUploadResponse, summary="Загрузить аудиофайл и получить URL для доступа", deprecated=True)
async def upload_audio(file: UploadFile = File(...)):
    return service.upload_audio(file)

@router.post("/process-audio", response_model=schemas.AudioUploadResponse, summary="Загрузить аудиофайл, расшифровать и сохранить в базу данных")
async def process_audio(
    id_question: int = Form(...),
    id_result: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await service.process_audio(db, id_question, id_result, file)

@router.get("/get-all-audios", response_model=List[schemas.AudioBase], summary="Получить список всех аудиозаписей")
async def get_all_audios(db: Session = Depends(get_db)):
    return service.get_all_audios(db)