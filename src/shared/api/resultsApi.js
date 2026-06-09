import { apiFetch } from './authApi';

const BASE = '/api/results';

const toJson = async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Ошибка запроса');
    return data;
};

export const resultsApi = {
    getByDisciplineAndYear: (disciplineId, year) =>
        apiFetch(`${BASE}/filter/discipline/${disciplineId}/year/${year}`).then(toJson),

    start: (id_student, id_test) => apiFetch(`${BASE}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_student, id_test }),
    }).then(toJson),

    calculate: (id_result) => apiFetch(`${BASE}/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_result }),
    }).then(toJson),

    setFinalGrade: (id_result, final_grade) => apiFetch(`${BASE}/${id_result}/final-grade`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ final_grade }),
    }).then(toJson),
};
