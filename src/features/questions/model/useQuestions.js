import { useState, useRef } from 'react';
import { storage } from '../../../shared/lib/storage';

const STORAGE_KEY = 'questions_data';
const loadData = () => storage.get(STORAGE_KEY) ?? { questions: [] };
const saveData = (data) => storage.set(STORAGE_KEY, data);

export const useQuestions = () => {
    const [questions, setQuestions] = useState(() => loadData().questions);
    const [addModalOpen, setAddModalOpen] = useState(false);
    const [editModalOpen, setEditModalOpen] = useState(false);
    const [editingQuestion, setEditingQuestion] = useState(null);
    const [pendingQuestions, setPendingQuestions] = useState([]); // загруженные из файла, без коэф.
    const fileInputRef = useRef(null);

    const persist = (newQuestions) => {
        setQuestions(newQuestions);
        saveData({ questions: newQuestions });
    };

    const addQuestion = ({ name, weight }) => {
        persist([...questions, { id: Date.now(), name, weight }]);
        setAddModalOpen(false);
    };

    const openEdit = (question) => {
        setEditingQuestion(question);
        setEditModalOpen(true);
    };

    const saveEdit = ({ name, weight, referenceAnswer }) => {
        persist(questions.map((q) =>
            q.id === editingQuestion.id ? { ...q, name, weight, referenceAnswer } : q
        ));
        setEditModalOpen(false);
        setEditingQuestion(null);
    };

    const deleteQuestion = (id) => {
        persist(questions.filter((q) => q.id !== id));
    };

    const loadFromFile = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            const lines = ev.target.result.split('\n').map((l) => l.trim()).filter(Boolean);
            setPendingQuestions(lines.map((name) => ({ id: Date.now() + Math.random(), name, weight: null })));
        };
        reader.readAsText(file);
        e.target.value = '';
    };

    const savePending = () => {
        persist([...questions, ...pendingQuestions]);
        setPendingQuestions([]);
    };

    const cancelPending = () => setPendingQuestions([]);

    return {
        questions, pendingQuestions,
        addModalOpen, setAddModalOpen,
        editModalOpen, setEditModalOpen,
        editingQuestion,
        addQuestion, openEdit, saveEdit, deleteQuestion,
        fileInputRef, loadFromFile,
        savePending, cancelPending,
    };
};