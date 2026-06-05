import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/AuthContext';

const INITIAL_DISCIPLINES = [
    { id: 1, name: 'Компьютерные сети', active: true },
    { id: 2, name: 'Распределенные задачи и алгоритмы', active: false },
    { id: 3, name: 'Компьютерные сети', active: false },
    { id: 4, name: 'Компьютерные сети', active: false },
    { id: 5, name: 'Компьютерные сети', active: false },
    { id: 6, name: 'Компьютерные сети', active: false },
];

export const useSettings = (correntUser) => {
    // const storageKey = `settings_${currentUser}`;
    const [manualCount, setManualCount] = useState('');
    const [autoCount, setAutoCount] = useState('');
    const [disciplines, setDisciplines] = useState(INITIAL_DISCIPLINES);
    const navigate = useNavigate();
    const { logout: authLogout } = useAuth();

    // useEffect(() => {
    //     const saved = storage.get(storageKey);
    //     if (saved) {
    //         setManualCount(saved.manualCount ?? '');
    //         setAutoCount(saved.autoCount ?? '');
    //         if (saved.disciplines) setDisciplines(saved.disciplines);
    //     }
    // }, [storageKey]);

    // useEffect(() => {
    //     storage.set(storageKey, { manualCount, autoCount, disciplines });
    // }, [manualCount, autoCount, storageKey, disciplines]);

    const toggleActive = (id) => {
        setDisciplines((prev) =>
            prev.map((d) => ({ ...d, active: d.id === id ? !d.active : false }))
        );
    };

    const handleManualCount = (e) => {
        const val = e.target.value;
        if (val === '' || parseInt(val) > 0) {
            setManualCount(val);
        }
    };

    const handleAutoCount = (e) => {
        const val = e.target.value;
        if (val === '' || parseInt(val) > 0) {
            setAutoCount(val);
        }
    };

    const addDiscipline = () => {
        const name = prompt('Название дисциплины:');
        if (!name?.trim()) return;
        setDisciplines((prev) => [
            ...prev,
            { id: Date.now(), name: name.trim(), active: false },
        ]);
    };

    const editDiscipline = (id) => {
        const discipline = disciplines.find((d) => d.id === id);
        const name = prompt('Новое название:', discipline.name);
        if (!name?.trim()) return;
        setDisciplines((prev) =>
            prev.map((d) => (d.id === id ? { ...d, name: name.trim() } : d))
        );
    };

    const deleteDiscipline = (id) => {
        setDisciplines((prev) => prev.filter((d) => d.id !== id));
    };

    const logout = async () => {
        await authLogout();
        navigate('/login');
    };

    return {
        manualCount, setManualCount,
        handleManualCount,
        autoCount, setAutoCount,
        handleAutoCount,
        disciplines,
        addDiscipline,
        editDiscipline,
        deleteDiscipline,
        logout,
        toggleActive,
    };
};