import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/AuthContext';
import { storage } from '../../../shared/lib/storage';
import { disciplinesApi } from '../../../shared/api/disciplinesApi';

export const useSettings = (currentUser) => {
    const storageKey = `settings_${currentUser}`;
    const saved = storage.get(storageKey);

    const [manualCount, setManualCount] = useState(saved?.manualCount ?? '');
    const [autoCount, setAutoCount] = useState(saved?.autoCount ?? '');
    const [disciplines, setDisciplines] = useState([]);
    const [activeDisciplineId, setActiveDisciplineId] = useState(saved?.activeDisciplineId ?? null);

    const navigate = useNavigate();
    const { logout: authLogout } = useAuth();

    useEffect(() => {
        disciplinesApi.getAll()
            .then((data) => setDisciplines(data))
            .catch(() => {});
    }, []);

    useEffect(() => {
        storage.set(storageKey, { manualCount, autoCount, activeDisciplineId });
    }, [manualCount, autoCount, activeDisciplineId, storageKey]);

    const toggleActive = (id) => {
        setActiveDisciplineId((prev) => (prev === id ? null : id));
    };

    const handleManualCount = (e) => {
        const val = e.target.value;
        if (val === '' || parseInt(val) > 0) setManualCount(val);
    };

    const handleAutoCount = (e) => {
        const val = e.target.value;
        if (val === '' || parseInt(val) > 0) setAutoCount(val);
    };

    const addDiscipline = async () => {
        const name = prompt('Название дисциплины:');
        if (!name?.trim()) return;
        try {
            const created = await disciplinesApi.create(name.trim());
            setDisciplines((prev) => [...prev, created]);
        } catch (e) {
            alert(e.message);
        }
    };

    const editDiscipline = async (id) => {
        try {
            const current = await disciplinesApi.getById(id);
            const name = prompt('Новое название:', current.name_discipline);
            if (!name?.trim()) return;
            const updated = await disciplinesApi.update(id, name.trim());
            setDisciplines((prev) => prev.map((d) => (d.id_discipline === id ? updated : d)));
        } catch (e) {
            alert(e.message);
        }
    };

    const deleteDiscipline = async (id) => {
        try {
            await disciplinesApi.delete(id);
            setDisciplines((prev) => prev.filter((d) => d.id_discipline !== id));
            if (activeDisciplineId === id) setActiveDisciplineId(null);
        } catch (e) {
            alert(e.message);
        }
    };

    const logout = async () => {
        await authLogout();
        navigate('/login');
    };

    const disciplinesWithActive = disciplines.map((d) => ({
        ...d,
        active: d.id_discipline === activeDisciplineId,
    }));

    return {
        manualCount, setManualCount, handleManualCount,
        autoCount, setAutoCount, handleAutoCount,
        disciplines: disciplinesWithActive,
        addDiscipline, editDiscipline, deleteDiscipline,
        logout, toggleActive,
    };
};
