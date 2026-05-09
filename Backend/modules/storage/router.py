import boto3
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from typing import List


from database import get_db

from . import models, schemas

from speech_to_text.speech_to_text_main.speach_to_text_new import run_stt_pipeline
from speech_to_text.speech_to_text_main.config import MODEL_DIR

load_dotenv()

router = APIRouter(prefix="/storage", tags=["Storage"])

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    endpoint_url=os.getenv("S3_ENDPOINT")
)

@router.post("/upload-audio", response_model=schemas.AudioUploadResponse, summary="Загрузить аудиофайл и получить URL для доступа", deprecated=True)
async def upload_audio(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Файл должен быть аудиозаписью")

    filename = file.filename

    try:
        s3_client.upload_fileobj(
            file.file,
            os.getenv("S3_BUCKET_NAME"),
            filename,
            ExtraArgs={'ContentType': file.content_type}
        )
        
        bucket = os.getenv("S3_BUCKET_NAME")
        endpoint = os.getenv("S3_ENDPOINT").replace("https://", "")
        file_url = f"https://{bucket}.{endpoint}/{filename}"
        
        return {"url": file_url, "filename": filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")

@router.post("/process-audio", response_model=schemas.AudioUploadResponse, summary="Загрузить аудиофайл, расшифровать и сохранить в базу данных")
async def process_audio(
    id_question: int = Form(...),
    id_result: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Файл должен быть аудиозаписью")

    try:
        audio_bytes = await file.read()
        
        bucket = os.getenv("S3_BUCKET_NAME")
        filename = file.filename
        
        s3_client.put_object(
            Bucket=bucket,
            Key=filename,
            Body=audio_bytes,
            ContentType=file.content_type
        )
        
        endpoint = os.getenv("S3_ENDPOINT").replace("https://", "").replace("http://", "")
        file_url = f"https://{bucket}.{endpoint}/{filename}"
        transcript_text = run_stt_pipeline(audio_bytes, str(MODEL_DIR))
        
        new_audio = models.Audio(
            id_question=id_question,
            id_result=id_result,
            filename=file_url,
            transcript=transcript_text
        )
        
        db.add(new_audio)
        db.commit()
        db.refresh(new_audio)
        
        return {
            "url": file_url,
            "filename": filename,
            "id_audio": new_audio.id_audio
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке: {str(e)}")


@router.get("/get-all-audios", response_model=List[schemas.AudioBase], summary="Получить список всех аудиозаписей")
async def get_all_audios(db: Session = Depends(get_db)):
    try:
        audios = db.query(models.Audio).all()
        if not audios:
            return []

        return audios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Не удалось получить список аудио: {str(e)}")