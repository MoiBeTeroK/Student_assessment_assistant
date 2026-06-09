import os
import time
import uuid
import httpx
from fastapi import HTTPException, status

OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL  = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
MODEL     = "GigaChat"

_token: str | None = None
_token_expires_at: float = 0


async def _get_token() -> str:
    global _token, _token_expires_at
    if _token and time.time() < _token_expires_at - 60:
        return _token

    credentials = os.getenv("GIGACHAT_CREDENTIALS", "").strip()
    scope       = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS").strip()

    if not credentials:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "GigaChat: переменная GIGACHAT_CREDENTIALS не задана на сервере")

    async with httpx.AsyncClient(verify=False) as client:
        try:
            r = await client.post(
                OAUTH_URL,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "RqUID": str(uuid.uuid4()),
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"scope": scope},
                timeout=15,
            )
        except httpx.RequestError as e:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f"GigaChat недоступен: {e}")

    if not r.is_success:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"GigaChat OAuth ошибка: {r.text}")

    body = r.json()
    _token = body["access_token"]
    # expires_at — Unix timestamp в миллисекундах, переводим в секунды
    _token_expires_at = body["expires_at"] / 1000 if "expires_at" in body else time.time() + 1800
    return _token


async def _chat(prompt: str) -> str:
    token = await _get_token()
    async with httpx.AsyncClient(verify=False) as client:
        try:
            r = await client.post(
                CHAT_URL,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
                timeout=60,
            )
        except httpx.RequestError as e:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, f"GigaChat недоступен: {e}")

    if not r.is_success:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"GigaChat ошибка: {r.text}")

    return r.json()["choices"][0]["message"]["content"].strip()


async def generate_standard_answer(question_text: str, discipline_name: str) -> str:
    prompt = (
        "Ты — опытный преподаватель высшего учебного заведения. "
        "Твоя задача — написать эталонный ответ на экзаменационный вопрос по дисциплине, которую я укажу.\n"
        "Строго соблюдай следующие правила:\n"
        "Ответ должен быть написан в виде связного текста без маркированных списков, нумерации и заголовков. "
        "Не должны использоваться никакие декораторы текста (курсив, полужирный и т.д.)\n"
        "Объём ответа — минимум 15 предложений, оптимальное число – 20 предложений. "
        "Ответ должен соответствовать тому, что студент способен произнести устно за 5–7 минут.\n"
        "Отвечай строго в рамках заданного вопроса. Не добавляй материал из смежных тем, явно не упомянутых в вопросе.\n"
        "Не включай в ответ примеры и иллюстрации, которые явно не следуют из формулировки вопроса.\n"
        "Не добавляй вводные фразы и обращения.\n\n"
        f"Дисциплина: {discipline_name}\n"
        f"Вопрос: {question_text}"
    )
    return await _chat(prompt)


async def generate_comment(questions_data: list[dict], rec_grade: int) -> str:
    questions_block = ""
    for i, item in enumerate(questions_data, start=1):
        questions_block += (
            f"Вопрос {i}: {item['question']}\n"
            f"Эталонный ответ {i}: {item['standard_answer']}\n"
            f"Ответ студента {i}: {item['transcript'] or 'Ответ не записан'}\n\n"
        )

    prompt = (
        "Ты — ассистент преподавателя высшего учебного заведения. "
        "Твоя задача — сформировать аналитический комментарий к ответам студента на вопросы экзаменационного билета.\n"
        "Строго соблюдай следующие правила:\n"
        "Не изменяй и не оспаривай рекомендуемую оценку. "
        "Твоя задача — обосновать именно её, опираясь на конкретные расхождения между ответами студента и эталонными ответами.\n"
        "Анализируй все вопросы билета в совокупности. Комментарий должен отражать общее качество ответов, а не отдельный вопрос.\n"
        "Ссылайся только на то, что явно присутствует в текстах ответов студента. "
        "Не приписывай ему ошибки или знания, которых нет в его ответах.\n"
        "Используй нейтральный академический тон. Комментарий адресован преподавателю, а не студенту.\n"
        "Не давай студенту советов и рекомендаций.\n"
        "Блок сильных сторон обязателен при любом качестве ответов: укажи, что было отвечено верно или частично верно.\n"
        "Структура ответа должна строго соответствовать следующему формату:\n"
        "Обоснование оценки: [2–3 предложения с конкретными ссылками на расхождения с эталонами]\n"
        "Недостатки: [перечень конкретных пробелов по вопросам билета]\n"
        "Сильные стороны: [что было отвечено верно или частично верно]\n\n"
        f"Рекомендуемая оценка: {rec_grade}. Эту оценку не изменять.\n\n"
        f"{questions_block}"
        "Сформируй аналитический комментарий строго в соответствии с заданной структурой."
    )
    return await _chat(prompt)
