import { useState } from 'react';
import { storage } from '../../../shared/lib/storage';

const STORAGE_KEY = 'tickets_data';
const loadData = () => storage.get(STORAGE_KEY) ?? { tickets: [] };
const saveData = (data) => storage.set(STORAGE_KEY, data);

export const useTickets = () => {
    const [tickets, setTickets] = useState(() => loadData().tickets);
    const [autoMode, setAutoMode] = useState(false);
    const [autoModalOpen, setAutoModalOpen] = useState(false);
    const [autoCount, setAutoCount] = useState('');
    const [questionSelectOpen, setQuestionSelectOpen] = useState(false);
    const [editingTicket, setEditingTicket] = useState(null);
    const [selectedQuestionIds, setSelectedQuestionIds] = useState([]);
    const [deleteTarget, setDeleteTarget] = useState(null);

    // Лимит вопросов из настроек
    const getManualLimit = () => {
        const settings = storage.get('settings_admin');
        return settings?.manualCount ? parseInt(settings.manualCount) : Infinity;
    };

    const persist = (newTickets) => {
        setTickets(newTickets);
        saveData({ tickets: newTickets });
    };

    // --- Автоматический режим ---
    const handleAutoToggle = () => {
        if (!autoMode) {
            // Включаем — открываем модалку, но галочку НЕ ставим пока
            setAutoModalOpen(true);
        } else {
            setAutoMode(false);
        }
    };

    const handleAutoModalClose = () => {
        // Закрыли без сохранения — галочка не ставится
        setAutoModalOpen(false);
        setAutoCount('');
    };

    const handleAutoGenerate = async () => {
        const questionsPerTicket = storage.get('settings_admin')?.autoCount ?? 3;
        try {
            await new Promise((r) => setTimeout(r, 800));
            const generated = Array.from({ length: Number(autoCount) }, (_, i) => ({
                id: Date.now() + i,
                name: `Билет №${tickets.length + i + 1}`,
                questionIds: [],
            }));
            persist([...tickets, ...generated]);
            setAutoMode(true);
        } catch (e) {
            console.error(e);
        } finally {
            setAutoModalOpen(false);
            setAutoCount('');
        }
    };

    const openCreate = () => {
        setEditingTicket(null);
        setSelectedQuestionIds([]);
        setQuestionSelectOpen(true);
    };

    const openEdit = (ticket) => {
        setEditingTicket(ticket);
        setSelectedQuestionIds(ticket.questionIds ?? []);
        setQuestionSelectOpen(true);
    };

    const toggleQuestion = (id) => {
        const limit = getManualLimit();
        setSelectedQuestionIds((prev) => {
            if (prev.includes(id)) return prev.filter((q) => q !== id);
            if (prev.length >= limit) return prev;
            return [...prev, id];
        });
    };

    const saveTicket = () => {
        if (editingTicket) {
            persist(tickets.map((t) =>
                t.id === editingTicket.id ? { ...t, questionIds: selectedQuestionIds } : t
            ));
        } else {
            persist([...tickets, {
                id: Date.now(),
                name: `Билет №${tickets.length + 1}`,
                questionIds: selectedQuestionIds,
            }]);
        }
        setQuestionSelectOpen(false);
        setEditingTicket(null);
    };

    const cancelSelect = () => {
        setQuestionSelectOpen(false);
        setEditingTicket(null);
    };

    const askDelete = (id) => setDeleteTarget(id);
    const cancelDelete = () => setDeleteTarget(null);
    const confirmDelete = () => {
        persist(tickets.filter((t) => t.id !== deleteTarget));
        setDeleteTarget(null);
    };

    return {
        tickets, autoMode, handleAutoToggle,
        autoModalOpen, handleAutoModalClose, autoCount, setAutoCount, handleAutoGenerate,
        questionSelectOpen, editingTicket,
        selectedQuestionIds, toggleQuestion, saveTicket, cancelSelect, openCreate, openEdit,
        deleteTarget, askDelete, cancelDelete, confirmDelete,
        getManualLimit,
    };
};