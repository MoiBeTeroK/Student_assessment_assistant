import { useState, useEffect, useRef } from 'react';
import { storage } from '../../../shared/lib/storage';
import { questionsApi } from '../../../shared/api/questionsApi';

const getActiveDisciplineId = () => storage.get('settings_admin')?.activeDisciplineId ?? null;

export const useQuestions = () => {
    const [questions, setQuestions] = useState([]);
    const [pendingQuestions, setPendingQuestions] = useState([]);
    const [addModalOpen, setAddModalOpen] = useState(false);
    const [editModalOpen, setEditModalOpen] = useState(false);
    const [editingQuestion, setEditingQuestion] = useState(null);
    const fileInputRef = useRef(null);

    const disciplineId = getActiveDisciplineId();

    useEffect(() => {
        if (!disciplineId) return;
        questionsApi.getByDiscipline(disciplineId)
            .then((data) => setQuestions(data))
            .catch(() => {});
    }, [disciplineId]);

    // Добавление вопроса вручную — сразу сохраняем через batch
    const addQuestion = async ({ question_content, complexity_score, standard_answer }) => {
        if (!disciplineId) return;
        try {
            const created = await questionsApi.batch([{
                id_discipline: disciplineId,
                question_content,
                complexity_score: complexity_score || null,
                standard_answer: standard_answer || null,
            }]);
            setQuestions((prev) => [...prev, ...created]);
            setAddModalOpen(false);
        } catch (e) {
            alert(e.message);
        }
    };

    const openEdit = (question) => {
        setEditingQuestion(question);
        setEditModalOpen(true);
    };

    // Редактирование — batch с id_question обновляет существующий
    const saveEdit = async ({ question_content, complexity_score, standard_answer }) => {
        if (!disciplineId) return;
        try {
            const updated = await questionsApi.batch([{
                id_question: editingQuestion.id_question,
                id_discipline: disciplineId,
                question_content,
                complexity_score: complexity_score || null,
                standard_answer: standard_answer || null,
            }]);
            setQuestions((prev) =>
                prev.map((q) => q.id_question === editingQuestion.id_question ? updated[0] : q)
            );
            setEditModalOpen(false);
            setEditingQuestion(null);
        } catch (e) {
            alert(e.message);
        }
    };

    const deleteQuestion = async (id_question) => {
        try {
            await questionsApi.delete(id_question);
            setQuestions((prev) => prev.filter((q) => q.id_question !== id_question));
        } catch (e) {
            alert(e.message);
        }
    };

    // Загрузка из файла — preview (без сохранения в БД)
    const loadFromFile = async (e) => {
        const file = e.target.files[0];
        if (!file || !disciplineId) return;
        e.target.value = '';
        try {
            const parsed = await questionsApi.parsePreview(disciplineId, file);
            setPendingQuestions(parsed.map((q, i) => ({ ...q, _tempId: Date.now() + i })));
        } catch (e) {
            alert(e.message);
        }
    };

    // Сохранение pending-вопросов из файла через batch
    const savePending = async () => {
        if (!disciplineId || !pendingQuestions.length) return;
        try {
            const payload = pendingQuestions.map(({ _tempId, ...q }) => q);
            const created = await questionsApi.batch(payload);
            setQuestions((prev) => [...prev, ...created]);
            setPendingQuestions([]);
        } catch (e) {
            alert(e.message);
        }
    };

    const cancelPending = () => setPendingQuestions([]);

    const clearAllQuestions = async () => {
        if (!disciplineId) return;
        if (!window.confirm('Удалить все вопросы дисциплины?')) return;
        try {
            await questionsApi.clearByDiscipline(disciplineId);
            setQuestions([]);
        } catch (e) {
            alert(e.message);
        }
    };

    const exportQuestions = async (format = 'docx') => {
        if (!disciplineId) return;
        try {
            const res = await questionsApi.export(disciplineId, format);
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `questions.${format}`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (e) {
            alert(e.message);
        }
    };

    return {
        questions,
        pendingQuestions,
        setPendingQuestions,
        disciplineId,
        addModalOpen, setAddModalOpen,
        editModalOpen, setEditModalOpen,
        editingQuestion,
        addQuestion, openEdit, saveEdit, deleteQuestion,
        fileInputRef, loadFromFile,
        savePending, cancelPending,
        exportQuestions,
        clearAllQuestions,
    };
};
