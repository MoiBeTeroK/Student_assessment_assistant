# from __future__ import annotations
# import re
# import logging
# from typing import Optional

# logger = logging.getLogger(__name__)

# _restorer_instance = None

# def init_punctuation():
#     global _restorer_instance
#     if _restorer_instance is None:
#         print("Предзагрузка модели пунктуации...")
#         _restorer_instance = PunctuationRestorer(use_gpu=False) 
#     return _restorer_instance

# def get_restorer():
#     if _restorer_instance is None:
#         return init_punctuation()
#     return _restorer_instance

# class PunctuationRestorer:
#     def __init__(self, use_gpu: bool = True):
#         try:
#             from deepmultilingualpunctuation import PunctuationModel
#             import torch
#         except ImportError:
#             raise ImportError(
#                 "Установи: pip install deepmultilingualpunctuation"
#             )

#         # Выбираем устройство
#         self.device = "cuda" if (use_gpu and torch.cuda.is_available()) else "cpu"

#         self._model = PunctuationModel(model="oliverguhr/fullstop-punctuation-multilang-large")
#         print("Модель пунктуации загружена.")

#     def restore(self, text: str) -> str:
#         """Восстановление знаков для отдельной строки"""
#         if not text or not text.strip():
#             return text

#         try:
#             result = self._model.restore_punctuation(text.strip())
#             return _post_process(result)
#         except Exception as e:
#             logger.warning(f"Ошибка пунктуации: {e}. Возвращаем оригинал.")
#             return text

#     def restore_segments(self, segments: list[dict]) -> list[dict]:
#         if not segments:
#             return []

#         texts = [seg.get("text", "").strip() for seg in segments if seg.get("text")]
        
#         if not texts:
#             return segments

#         full_text = " ".join(texts)
        
#         try:
#             restored_full = self._model.restore_punctuation(full_text)
#             processed_full = _post_process(restored_full)
#             for seg in segments:
#                 if seg.get("text"):
#                     seg["text"] = self.restore(seg["text"])
                    
#             return segments
            
#         except Exception as e:
#             logger.error(f"Критическая ошибка в restore_segments: {e}")
#             return segments


# def _post_process(text: str) -> str:
#     text = re.sub(r'\s+([\.,:;!?])', r'\1', text)
#     text = re.sub(r'\s{2,}', ' ', text)
#     text = text.strip()
#     text = _capitalize_sentences(text)
#     return text


# def _capitalize_sentences(text: str) -> str:
#     if not text:
#         return text

#     sentences = re.split(r'([\.\!\?]\s*)', text)
#     result = ""
#     for i in range(0, len(sentences), 2):
#         sentence = sentences[i]
#         punctuation = sentences[i+1] if i+1 < len(sentences) else ""
#         if sentence:
#             sentence = sentence[0].upper() + sentence[1:]
#         result += sentence + punctuation
        
#     return result

from __future__ import annotations
import os
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_restorer_instance = None

def init_punctuation():
    global _restorer_instance
    if _restorer_instance is None:
        print(" [Punctuation] Первая фиксация вызова. Начинается ленивая загрузка модели...")
        _restorer_instance = PunctuationRestorer(use_gpu=False) 
    return _restorer_instance


def get_restorer():
    if _restorer_instance is None:
        return init_punctuation()
    return _restorer_instance


class PunctuationRestorer:
    def __init__(self, use_gpu: bool = True):
        try:
            from deepmultilingualpunctuation import PunctuationModel
            import torch
        except ImportError:
            raise ImportError(
                "Установи: pip install deepmultilingualpunctuation"
            )

        # Выбираем устройство
        self.device = "cuda" if (use_gpu and torch.cuda.is_available()) else "cpu"
        
        self._model = PunctuationModel()
        print(" ✓ [Punctuation] Модель пунктуации успешно загружена.")

    def restore(self, text: str) -> str:
        """Восстановление знаков для отдельной строки"""
        if not text or not text.strip():
            return text

        try:
            result = self._model.restore_punctuation(text.strip())
            return _post_process(result)
        except Exception as e:
            logger.warning(f"Ошибка пунктуации: {e}. Возвращаем оригинал.")
            return text

    def restore_segments(self, segments: list[dict]) -> list[dict]:
        if not segments:
            return []

        # Проходим по каждому сегменту ОДИН раз
        for seg in segments:
            original_text = seg.get("text")
            
            if original_text and original_text.strip():
                # Модель вызывается строго по одному разу на сегмент
                try:
                    restored = self._model.restore_punctuation(original_text.strip())
                    seg["text"] = _post_process(restored)
                except Exception as segment_error:
                    logger.warning(f"Не удалось обработать сегмент: {segment_error}")
                    # В случае локального сбоя оставляем оригинальный текст, чтобы не рушить весь массив
                    seg["text"] = original_text

        return segments


def _post_process(text: str) -> str:
    text = re.sub(r'\s+([\.,:;!?])', r'\1', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    text = _capitalize_sentences(text)
    return text


def _capitalize_sentences(text: str) -> str:
    if not text:
        return text

    sentences = re.split(r'([\.\!\?]\s*)', text)
    result = ""
    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        punctuation = sentences[i+1] if i+1 < len(sentences) else ""
        if sentence:
            sentence = sentence[0].upper() + sentence[1:]
        result += sentence + punctuation
        
    return result