import { apiFetch } from './authApi';

const BASE = '/api/tests';

const toJson = async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Ошибка запроса');
    return data;
};

export const testsApi = {
    getAll: () => apiFetch(`${BASE}/`).then(toJson),
    getByDiscipline: (disciplineId) => apiFetch(`${BASE}/discipline/${disciplineId}`).then(toJson),
    create: (data) => apiFetch(`${BASE}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    }).then(toJson),
    update: (testId, data) => apiFetch(`${BASE}/${testId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    }).then(toJson),
    delete: async (testId) => {
        const res = await apiFetch(`${BASE}/${testId}`, { method: 'DELETE' });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || 'Ошибка удаления');
        }
    },
    generateConfirm: (data) => apiFetch(`${BASE}/generate-confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    }).then(toJson),
    export: async (disciplineId, format = 'docx') => {
        const res = await apiFetch(`${BASE}/export/tests/${disciplineId}?format=${format}`);
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || 'Ошибка экспорта');
        }
        return res;
    },
};
