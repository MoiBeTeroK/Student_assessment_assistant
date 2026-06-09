import { apiFetch } from './authApi';

const toJson = async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Ошибка GigaChat');
    return data;
};

export const gigachatApi = {
    generateAnswer: (id_question) =>
        apiFetch('/api/gigachat/generate-answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_question }),
        }).then(toJson),

    generateAnswerByText: (question_content, id_discipline) =>
        apiFetch('/api/gigachat/generate-answer-by-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question_content, id_discipline }),
        }).then(toJson),

    generateComment: (id_result) =>
        apiFetch('/api/gigachat/generate-comment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_result }),
        }).then(toJson),
};
