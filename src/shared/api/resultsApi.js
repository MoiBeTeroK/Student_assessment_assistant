import { apiFetch } from './authApi';

const BASE = '/api/results';

const toJson = async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Ошибка запроса');
    return data;
};

export const resultsApi = {
    start: (id_student, id_test) => apiFetch(`${BASE}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_student, id_test }),
    }).then(toJson),

    setFinalGrade: (id_result, final_grade) => apiFetch(`${BASE}/${id_result}/final-grade`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ final_grade }),
    }).then(toJson),
};
