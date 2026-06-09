import { useState, useEffect } from 'react';
import { storage } from '../../../shared/lib/storage';
import { testsApi } from '../../../shared/api/testsApi';
import { questionsApi } from '../../../shared/api/questionsApi';

const getSettings = () => storage.get('settings_admin') ?? {};

export const useTickets = () => {
    const [tickets, setTickets] = useState([]);
    const [questions, setQuestions] = useState([]);
    const [autoMode, setAutoModeState] = useState(() => storage.get('tickets_auto_mode') ?? false);

    const setAutoMode = (val) => {
        setAutoModeState(val);
        storage.set('tickets_auto_mode', val);
    };
    const [autoModalOpen, setAutoModalOpen] = useState(false);
    const [autoCount, setAutoCount] = useState('');
    const [questionSelectOpen, setQuestionSelectOpen] = useState(false);
    const [editingTicket, setEditingTicket] = useState(null);
    const [selectedQuestionIds, setSelectedQuestionIds] = useState([]);
    const [deleteTarget, setDeleteTarget] = useState(null);

    const disciplineId = getSettings().activeDisciplineId ?? null;

    useEffect(() => {
        if (!disciplineId) return;
        testsApi.getByDiscipline(disciplineId)
            .then(setTickets)
            .catch(() => {});
        questionsApi.getByDiscipline(disciplineId)
            .then(setQuestions)
            .catch(() => {});
    }, [disciplineId]);

    // Автоматическое добавление доступно только если у всех вопросов есть complexity_score
    const allQuestionsHaveScore = questions.length > 0 && questions.every((q) => q.complexity_score != null);

    const getManualLimit = () => {
        const s = getSettings();
        return s.manualCount ? parseInt(s.manualCount) : 3;
    };

    // Лимит зависит от режима: ручной → manualCount, авто → autoCount
    const getEffectiveLimit = () => {
        const s = getSettings();
        if (autoMode) return s.autoCount ? parseInt(s.autoCount) : 3;
        return s.manualCount ? parseInt(s.manualCount) : 3;
    };

    // --- Автоматический режим ---
    const handleAutoToggle = () => {
        if (!allQuestionsHaveScore) return;
        if (!autoMode) {
            setAutoModalOpen(true);
        } else {
            setAutoMode(false);
        }
    };

    const handleAutoModalClose = () => {
        setAutoModalOpen(false);
        setAutoCount('');
    };

    const handleAutoGenerate = async () => {
        const s = getSettings();
        const questionsPerTest = parseInt(s.autoCount) || 3;
        try {
            const generated = await testsApi.generateConfirm({
                id_discipline: disciplineId,
                num_tests: parseInt(autoCount),
                questions_per_test: questionsPerTest,
            });
            setTickets((prev) => [...prev, ...generated]);
            setAutoMode(true);
        } catch (e) {
            alert(e.message || 'Ошибка генерации');
        } finally {
            setAutoModalOpen(false);
            setAutoCount('');
        }
    };

    // --- Ручное создание / редактирование ---
    const openCreate = () => {
        setEditingTicket(null);
        setSelectedQuestionIds([]);
        setQuestionSelectOpen(true);
    };

    const openEdit = (ticket) => {
        setEditingTicket(ticket);
        setSelectedQuestionIds(ticket.questions?.map((q) => q.id_question) ?? []);
        setQuestionSelectOpen(true);
    };

    const toggleQuestion = (id) => {
        const limit = getEffectiveLimit();
        setSelectedQuestionIds((prev) => {
            if (prev.includes(id)) return prev.filter((q) => q !== id);
            if (prev.length >= limit) return prev;
            return [...prev, id];
        });
    };

    const saveTicket = async () => {
        if (!disciplineId) return;
        try {
            if (editingTicket) {
                const updated = await testsApi.update(editingTicket.id_test, {
                    question_ids: selectedQuestionIds,
                });
                setTickets((prev) => prev.map((t) => t.id_test === editingTicket.id_test ? updated : t));
            } else {
                const nextNumber = tickets.length > 0
                    ? Math.max(...tickets.map((t) => t.test_number)) + 1
                    : 1;
                const created = await testsApi.create({
                    test_number: nextNumber,
                    id_discipline: disciplineId,
                    question_ids: selectedQuestionIds,
                });
                // API возвращает только id_test, достраиваем полный объект
                const fullTicket = {
                    id_test: created.id_test,
                    test_number: nextNumber,
                    id_discipline: disciplineId,
                    questions: questions.filter((q) => selectedQuestionIds.includes(q.id_question)),
                };
                setTickets((prev) => [...prev, fullTicket]);
            }
        } catch (e) {
            alert(e.message);
        }
        setQuestionSelectOpen(false);
        setEditingTicket(null);
    };

    const cancelSelect = () => {
        setQuestionSelectOpen(false);
        setEditingTicket(null);
    };

    // --- Удаление ---
    const askDelete = (id) => setDeleteTarget(id);
    const cancelDelete = () => setDeleteTarget(null);
    const confirmDelete = async () => {
        try {
            await testsApi.delete(deleteTarget);
            setTickets((prev) => prev.filter((t) => t.id_test !== deleteTarget));
        } catch (e) {
            alert(e.message);
        }
        setDeleteTarget(null);
    };

    // --- Экспорт ---
    const exportTickets = async (format = 'docx') => {
        if (!disciplineId) return;
        try {
            const res = await testsApi.export(disciplineId, format);
            const cd = res.headers.get('Content-Disposition') ?? '';
            const rfcMatch = cd.match(/filename\*=UTF-8''(.+)/i);
            const plainMatch = cd.match(/filename="?([^";\n]+)"?/i);
            const filename = rfcMatch
                ? decodeURIComponent(rfcMatch[1])
                : plainMatch
                ? plainMatch[1]
                : `tickets.${format}`;
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        } catch (e) {
            alert(e.message);
        }
    };

    return {
        tickets, questions, disciplineId,
        allQuestionsHaveScore,
        autoMode, handleAutoToggle,
        autoModalOpen, handleAutoModalClose, autoCount, setAutoCount, handleAutoGenerate,
        questionSelectOpen, editingTicket,
        selectedQuestionIds, toggleQuestion, saveTicket, cancelSelect, openCreate, openEdit,
        deleteTarget, askDelete, cancelDelete, confirmDelete,
        getManualLimit, getEffectiveLimit, exportTickets,
    };
};
