import torch
import librosa
import os
import tempfile
import re
from transformers import AutoProcessor, AutoModelForCTC
from .diarization_silera_ecapa import get_speech_segments # импорт упрощенного VAD

processor = None
model = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def init_asr(model_path):
    global processor, model
    if processor is None:
        processor = AutoProcessor.from_pretrained(model_path)
        model = AutoModelForCTC.from_pretrained(model_path).to(device)
        model.eval()

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'<unk>', '', text)
    return text.strip()

def run_stt_pipeline(audio_bytes: bytes, model_path: str):
    init_asr(model_path)
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = tmp_file.name

    try:
        # Получаем точные границы речи через VAD
        segments = get_speech_segments(tmp_path)
        if not segments:
            return "Речь не распознана."

        wav, sr = librosa.load(tmp_path, sr=16000)
        recognized_segments = []

        # Распознаем каждый сегмент
        for seg in segments:
            s_idx, e_idx = int(seg["start"] * sr), int(seg["end"] * sr)
            chunk = wav[s_idx:e_idx]
            
            inputs = processor(chunk, sampling_rate=16000, return_tensors="pt", padding=True)
            with torch.no_grad():
                logits = model(inputs.input_values.to(device)).logits
            
            pred_ids = torch.argmax(logits, dim=-1)[0]
            text = processor.decode(pred_ids, skip_special_tokens=True)
            text = clean_text(text)
            
            if text:
                recognized_segments.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": text,
                    "speaker": "SPEAKER_0"
                })

        # Восстановление пунктуации
        try:
            from .punctuation import get_restorer
            restorer = get_restorer()
            recognized_segments = restorer.restore_segments(recognized_segments)
        except Exception as e:
            import traceback
            traceback.print_exc()

        # Собираем финальный текст
        full_text = " ".join([s["text"] for s in recognized_segments])
        return full_text if full_text else "Голос обнаружен, но слова не распознаны."

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)