import { apiFetch } from './authApi';

const toJsonUsers = async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Ошибка запроса');
    return data;
};

export const usersApi = {
    getMe: () => apiFetch('/api/auth/me/').then(toJsonUsers),
};

const BASE = '/api/students';

const toJson = async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Ошибка запроса');
    return data;
};

export const studentsApi = {
    getAll: () => apiFetch(`${BASE}/`).then(toJson),
    getById: (id) => apiFetch(`${BASE}/${id}`).then(toJson),
    update: (id, data) => apiFetch(`${BASE}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    }).then(toJson),
    delete: (id) => apiFetch(`${BASE}/${id}`, { method: 'DELETE' }).then(toJson),
    batch: (students) => apiFetch(`${BASE}/batch`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(students),
    }).then(toJson),
    importFromFile: (file) => {
        const form = new FormData();
        form.append('file', file);
        return apiFetch(`${BASE}/import-from-file`, {
            method: 'POST',
            body: form,
        }).then(toJson);
    },
};
