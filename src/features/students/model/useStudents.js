import { useState, useRef } from 'react';
import { storage } from '../../../shared/lib/storage';

const STORAGE_KEY = 'students_data';

const loadData = () => storage.get(STORAGE_KEY) ?? { groups: [] };
const saveData = (data) => storage.set(STORAGE_KEY, data);

export const useStudents = () => {
    const [groups, setGroups] = useState(() => loadData().groups);
    const [selectedGroup, setSelectedGroup] = useState(null);
    const [isAdding, setIsAdding] = useState(false);       // добавление новой группы
    const [newGroupName, setNewGroupName] = useState('');
    const [addingStudent, setAddingStudent] = useState(false); // добавление студента
    const [newStudentName, setNewStudentName] = useState('');
    const [deleteTarget, setDeleteTarget] = useState(null);  // id группы для удаления
    const [editingGroupId, setEditingGroupId] = useState(null);
    const [editingGroupName, setEditingGroupName] = useState('');
    const fileInputRef = useRef(null);
    const [editingStudentId, setEditingStudentId] = useState(null);
    const [editingStudentName, setEditingStudentName] = useState('');

    const persist = (newGroups) => {
        setGroups(newGroups);
        saveData({ groups: newGroups });
    };

    const startAddGroup = () => {
        setIsAdding(true);
        setNewGroupName('');
    };

    const confirmAddGroup = () => {
        if (!newGroupName.trim()) { setIsAdding(false); return; }
        const newGroup = { id: Date.now(), name: newGroupName.trim(), students: [] };
        persist([...groups, newGroup]);
        setIsAdding(false);
    };

    const handleGroupKeyDown = (e) => {
        if (e.key === 'Enter') confirmAddGroup();
        if (e.key === 'Escape') {
            e.preventDefault();
            setIsAdding(false);
            setNewGroupName('');
        }
    };

    const startEditGroup = (id) => {
        const group = groups.find((g) => g.id === id);
        const name = prompt('Новое название:', group.name);
        if (!name?.trim()) return;
        persist(groups.map((g) => g.id === id ? { ...g, name: name.trim() } : g));
    };

    const confirmEditGroup = () => {
        if (!editingGroupName.trim()) { setEditingGroupId(null); return; }
        persist(groups.map((g) => g.id === editingGroupId ? { ...g, name: editingGroupName.trim() } : g));
        setEditingGroupId(null);
    };

    const handleEditGroupKeyDown = (e) => {
        if (e.key === 'Enter') confirmEditGroup();
        if (e.key === 'Escape') setEditingGroupId(null);
    };

    const askDeleteGroup = (id) => setDeleteTarget(id);
    const cancelDelete = () => setDeleteTarget(null);
    const confirmDelete = () => {
        persist(groups.filter((g) => g.id !== deleteTarget));
        if (selectedGroup?.id === deleteTarget) setSelectedGroup(null);
        setDeleteTarget(null);
    };

    const startAddStudent = () => {
        setAddingStudent(true);
        setNewStudentName('');
    };

    const confirmAddStudent = () => {
        if (!newStudentName.trim()) { setAddingStudent(false); return; }
        const updated = groups.map((g) =>
            g.id === selectedGroup.id
                ? { ...g, students: [...g.students, { id: Date.now(), name: newStudentName.trim() }] }
                : g
        );
        persist(updated);
        setSelectedGroup(updated.find((g) => g.id === selectedGroup.id));
        setAddingStudent(false);
    };

    const handleStudentKeyDown = (e) => {
        if (e.key === 'Enter') confirmAddStudent();
        if (e.key === 'Escape') setAddingStudent(false);
    };

    const saveStudents = () => {
        // здесь будет вызов API, пока просто сбрасываем состояние ввода
        setAddingStudent(false);
        setNewStudentName('');
    };

    const editStudent = (id) => {
        const student = selectedGroup.students.find((s) => s.id === id);
        const name = prompt('Новое ФИО:', student.name);
        if (!name?.trim()) return;
        const updated = groups.map((g) =>
            g.id === selectedGroup.id
                ? { ...g, students: g.students.map((s) => s.id === id ? { ...s, name: name.trim() } : s) }
                : g
        );
        persist(updated);
        setSelectedGroup(updated.find((g) => g.id === selectedGroup.id));
    };

    const deleteStudent = (id) => {
        const updated = groups.map((g) =>
            g.id === selectedGroup.id
                ? { ...g, students: g.students.filter((s) => s.id !== id) }
                : g
        );
        persist(updated);
        setSelectedGroup(updated.find((g) => g.id === selectedGroup.id));
    };

    const loadFromFile = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            const lines = ev.target.result.split('\n').map((l) => l.trim()).filter(Boolean);
            const newStudents = lines.map((name) => ({ id: Date.now() + Math.random(), name }));
            const updated = groups.map((g) =>
                g.id === selectedGroup.id ? { ...g, students: [...g.students, ...newStudents] } : g
            );
            persist(updated);
            setSelectedGroup(updated.find((g) => g.id === selectedGroup.id));
        };
        reader.readAsText(file);
        e.target.value = '';
    };

    return {
        groups,
        selectedGroup,
        setSelectedGroup,
        isAdding,
        newGroupName,
        setNewGroupName,
        startAddGroup,
        handleGroupKeyDown,
        editingGroupId,
        editingGroupName,
        setEditingGroupName,
        startEditGroup,
        handleEditGroupKeyDown,
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