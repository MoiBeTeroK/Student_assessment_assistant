import { useState, useEffect } from 'react';
import { storage } from '../../../shared/lib/storage';
import { resultsApi } from '../../../shared/api/resultsApi';
import { studentsApi } from '../../../shared/api/studentsApi';

const getActiveDisciplineId = () => storage.get('settings_admin')?.activeDisciplineId ?? null;

const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    const pad = (n) => String(n).padStart(2, '0');
    return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

export const useExamResults = () => {
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(false);
    const currentYear = new Date().getFullYear();
    const yearOptions = Array.from({ length: currentYear - 2020 + 1 }, (_, i) => currentYear - i);
    const [year, setYear] = useState(currentYear);

    const disciplineId = getActiveDisciplineId();

    useEffect(() => {
        if (!disciplineId || String(year).length !== 4) return;
        setLoading(true);
        setRows([]);

        Promise.all([
            resultsApi.getByDisciplineAndYear(disciplineId, year),
            studentsApi.getAll(),
        ])
            .then(([results, students]) => {
                const studentMap = Object.fromEntries(
                    students.map((s) => [s.id_student, s])
                );

                const mapped = results
                    .filter((r) => r.final_grade != null)
                    .map((r) => {
                        const s = studentMap[r.id_student];
                        const grp = s?.group_rel ?? s?.group;
                        return {
                            id_result: r.id_result,
                            name: s?.name ?? `Студент ${r.id_student}`,
                            group: grp?.group_name ?? '—',
                            rec_grade: r.rec_grade ?? '—',
                            final_grade: r.final_grade,
                            date: formatDate(r.date),
                        };
                    });

                setRows(mapped);
            })
            .catch(() => {})
            .finally(() => setLoading(false));
    }, [disciplineId, year]);

    const avgGrade = rows.length > 0
        ? (rows.reduce((sum, r) => sum + r.final_grade, 0) / rows.length).toFixed(2)
        : null;

    return { rows, loading, disciplineId, avgGrade, year, setYear, yearOptions };
};
