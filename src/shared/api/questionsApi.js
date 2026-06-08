import { apiFetch } from './authApi';

const BASE = '/api/questions';

const toJson = async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Ошибка запроса');
    return data;
};

export const questionsApi = {
    getByDiscipline: (disciplineId) =>
        apiFetch(`${BASE}/discipline/${disciplineId}`).then(toJson),

    delete: async (questionId) => {
        const res = await apiFetch(`${BASE}/${questionId}`, { method: 'DELETE' });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || 'Ошибка удаления');
        }
    },

    batch: (questions) => apiFetch(`${BASE}/batch`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(questions),
    }).then(toJson),

    parsePreview: (disciplineId, file) => {
        const form = new FormData();
        form.append('file', file);
        return apiFetch(`${BASE}/parse-preview/${disciplineId}`, {
            method: 'POST',
            body: form,
        }).then(toJson);
    },

    clearByDiscipline: async (disciplineId) => {
        const res = await apiFetch(`${BASE}/clear-discipline/${disciplineId}`, { method: 'DELETE' });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || 'Ошибка удаления');
        }
    },

    export: async (disciplineId, format = 'docx') => {
        const res = await apiFetch(`${BASE}/export/${disciplineId}?format=${format}`);
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || 'Ошибка экспорта');
        }
        return res;
    },
};
