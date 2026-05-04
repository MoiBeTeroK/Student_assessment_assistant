import boto3
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv
from modules.storage.schemas import AudioUploadResponse

load_dotenv()

router = APIRouter(prefix="/storage", tags=["Storage"])

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    endpoint_url=os.getenv("S3_ENDPOINT")
)

@router.post("/upload-audio", response_model=AudioUploadResponse, summary="Загрузить аудиофайл и получить URL для доступа")
async def upload_audio(file: UploadFile = File(...)):
    # Проверка, что это аудио
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