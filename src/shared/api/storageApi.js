import { apiFetch } from './authApi';

const toJson = async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Ошибка запроса');
    return data;
};

export const storageApi = {
    processAudio: (idQuestion, idResult, blob) => {
        const form = new FormData();
        form.append('id_question', idQuestion);
        form.append('id_result', idResult);
        form.append('file', blob, `question_${idQuestion}_${Date.now()}.wav`);
        return apiFetch('/storage/process-audio', {
            method: 'POST',
            body: form,
        }).then(toJson);
    },
};
