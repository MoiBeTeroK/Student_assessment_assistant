import { apiFetch } from './authApi';

const BASE = '/api/disciplines';

const toJson = async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Ошибка запроса');
    return data;
};

export const disciplinesApi = {
    getAll: () => apiFetch(`${BASE}/`).then(toJson),
    getById: (id) => apiFetch(`${BASE}/${id}`).then(toJson),
    create: (name) => apiFetch(`${BASE}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name_discipline: name }),
    }).then(toJson),
    update: (id, name) => apiFetch(`${BASE}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name_discipline: name }),
    }).then(toJson),
    delete: (id) => apiFetch(`${BASE}/${id}`, { method: 'DELETE' }).then(toJson),
};
