import { useState, useEffect, useRef } from 'react';
import { storage } from '../../../shared/lib/storage';
import { groupsApi } from '../../../shared/api/groupsApi';
import { studentsApi } from '../../../shared/api/studentsApi';

// localStorage хранит только несохранённых (pending) студентов: { [id_group]: [{id, name, pending: true}] }
const PENDING_KEY = 'pending_students_by_group';

const getPendingCache = () => storage.get(PENDING_KEY) ?? {};
const savePendingCache = (cache) => storage.set(PENDING_KEY, cache);

const getPendingForGroup = (id_group) => getPendingCache()[id_group] ?? [];
const setPendingForGroup = (id_group, students) => {
    savePendingCache({ ...getPendingCache(), [id_group]: students });
};
const clearPendingForGroup = (id_group) => {
    const cache = getPendingCache();
    delete cache[id_group];
    savePendingCache(cache);
};

// Маппинг студента из API → внутренний формат
// FastAPI сериализует поле с alias="group_rel" как group_rel в JSON
const fromApi = (s) => ({
    id: s.id_student,
    id_student: s.id_student,
    name: s.name,
    pending: false,
    group: s.group_rel ?? s.group,
});

export const useStudents = () => {
    const [groups, setGroups] = useState([]);
    const [selectedGroup, setSelectedGroupState] = useState(null);
    const [isAdding, setIsAdding] = useState(false);
    const [newGroupName, setNewGroupName] = useState('');
    const [addingStudent, setAddingStudent] = useState(false);
    const [newStudentName, setNewStudentName] = useState('');
    const [deleteTarget, setDeleteTarget] = useState(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        groupsApi.getAll()
            .then((data) => setGroups(data))
            .catch(() => {});
    }, []);

    // Выбор группы: загружаем студентов из API + pending из localStorage
    const selectGroup = async (group) => {
        try {
            const all = await studentsApi.getAll();
            const saved = all
                .filter((s) => {
                    // FastAPI сериализует alias "group_rel" в ключ group_rel
                    const g = s.group_rel ?? s.group;
                    return g?.id_group === group.id_group;
                })
                .map(fromApi);
            const pending = getPendingForGroup(group.id_group);
            setSelectedGroupState({ ...group, students: [...saved, ...pending] });
        } catch (e) {
            console.error('selectGroup error:', e);
            const pending = getPendingForGroup(group.id_group);
            setSelectedGroupState({ ...group, students: pending });
        }
    };

    const updateStudentsInState = (updater) => {
        setSelectedGroupState((prev) => ({ ...prev, students: updater(prev.students) }));
    };

    // --- Группы ---

    const startAddGroup = () => { setIsAdding(true); setNewGroupName(''); };

    const confirmAddGroup = async () => {
        if (!newGroupName.trim()) { setIsAdding(false); return; }
        try {
            const created = await groupsApi.create(newGroupName.trim());
            setGroups((prev) => [...prev, created]);
        } catch (e) { alert(e.message); }
        setIsAdding(false);
        setNewGroupName('');
    };

    const handleGroupKeyDown = (e) => {
        if (e.key === 'Enter') confirmAddGroup();
        if (e.key === 'Escape') { e.preventDefault(); setIsAdding(false); setNewGroupName(''); }
    };

    const startEditGroup = async (id) => {
        try {
            const current = await groupsApi.getById(id);
            const name = prompt('Новое название:', current.group_name);
            if (!name?.trim()) return;
            const updated = await groupsApi.update(id, name.trim());
            setGroups((prev) => prev.map((g) => g.id_group === id ? updated : g));
            if (selectedGroup?.id_group === id) {
                setSelectedGroupState((prev) => ({ ...prev, group_name: updated.group_name }));
            }
        } catch (e) { alert(e.message); }
    };

    const askDeleteGroup = (id) => setDeleteTarget(id);
    const cancelDelete = () => setDeleteTarget(null);
    const confirmDelete = async () => {
        try {
            await groupsApi.delete(deleteTarget);
            setGroups((prev) => prev.filter((g) => g.id_group !== deleteTarget));
            if (selectedGroup?.id_group === deleteTarget) setSelectedGroupState(null);
            clearPendingForGroup(deleteTarget);
        } catch (e) { alert(e.message); }
        setDeleteTarget(null);
    };

    // --- Студенты ---

    const startAddStudent = () => { setAddingStudent(true); setNewStudentName(''); };

    const confirmAddStudent = () => {
        if (!newStudentName.trim() || !selectedGroup) { setAddingStudent(false); return; }
        const newStudent = { id: Date.now(), name: newStudentName.trim(), pending: true };
        updateStudentsInState((prev) => {
            const updated = [...prev, newStudent];
            setPendingForGroup(selectedGroup.id_group, updated.filter((s) => s.pending));
            return updated;
        });
        setAddingStudent(false);
        setNewStudentName('');
    };

    const handleStudentKeyDown = (e) => {
        if (e.key === 'Enter') confirmAddStudent();
        if (e.key === 'Escape') setAddingStudent(false);
    };

    // Отправляет несохранённых студентов на бэкенд
    const saveStudents = async () => {
        setAddingStudent(false);
        if (!selectedGroup) return;

        const pending = selectedGroup.students.filter((s) => s.pending);
        if (!pending.length) return;

        try {
            const payload = pending.map((s) => ({
                name: s.name,
                group: { group_name: selectedGroup.group_name },
            }));
            const { students: created } = await studentsApi.batch(payload);
            const createdMapped = created.map(fromApi);

            updateStudentsInState((prev) => [
                ...prev.filter((s) => !s.pending),
                ...createdMapped,
            ]);
            clearPendingForGroup(selectedGroup.id_group);
        } catch (e) { alert(e.message); }
    };

    const editStudent = async (id) => {
        const student = selectedGroup.students.find((s) => s.id === id);
        const name = prompt('Новое ФИО:', student.name);
        if (!name?.trim()) return;

        if (student.pending) {
            updateStudentsInState((prev) => {
                const updated = prev.map((s) => s.id === id ? { ...s, name: name.trim() } : s);
                setPendingForGroup(selectedGroup.id_group, updated.filter((s) => s.pending));
                return updated;
            });
        } else {
            try {
                const result = await studentsApi.update(student.id_student, {
                    name: name.trim(),
                    id_group: selectedGroup.id_group,
                });
                updateStudentsInState((prev) =>
                    prev.map((s) => s.id === id ? fromApi(result) : s)
                );
            } catch (e) { alert(e.message); }
        }
    };

    const deleteStudent = async (id) => {
        const student = selectedGroup.students.find((s) => s.id === id);

        if (student.pending) {
            updateStudentsInState((prev) => {
                const updated = prev.filter((s) => s.id !== id);
                setPendingForGroup(selectedGroup.id_group, updated.filter((s) => s.pending));
                return updated;
            });
        } else {
            try {
                await studentsApi.delete(student.id_student);
                updateStudentsInState((prev) => prev.filter((s) => s.id !== id));
            } catch (e) { alert(e.message); }
        }
    };

    // Загрузка из файла через бэкенд (docx/pdf)
    const loadFromFile = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        e.target.value = '';
        try {
            const { students: imported } = await studentsApi.importFromFile(file);
            // Фильтруем только студентов текущей группы из ответа
            const forThisGroup = imported
                .filter((s) => (s.group_rel ?? s.group)?.id_group === selectedGroup.id_group)
                .map(fromApi);
            if (forThisGroup.length) {
                updateStudentsInState((prev) => {
                    const existingIds = new Set(prev.filter((s) => !s.pending).map((s) => s.id_student));
                    const newOnes = forThisGroup.filter((s) => !existingIds.has(s.id_student));
                    return [...prev, ...newOnes];
                });
            }
        } catch (e) { alert(e.message); }
    };

    return {
        groups,
        selectedGroup,
        setSelectedGroup: (val) => val ? selectGroup(val) : setSelectedGroupState(null),
        isAdding,
        newGroupName,
        setNewGroupName,
        startAddGroup,
        handleGroupKeyDown,
        startEditGroup,
        deleteTarget,
        askDeleteGroup,
        cancelDelete,
        confirmDelete,
        addingStudent,
        newStudentName,
        setNewStudentName,
        startAddStudent,
        handleStudentKeyDown,
        fileInputRef,
        loadFromFile,
        setIsAdding,
        saveStudents,
        editStudent,
        deleteStudent,
    };
};
