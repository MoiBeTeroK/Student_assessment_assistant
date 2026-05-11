import Box from '@mui/material/Box';
import { Check as CheckIcon } from '@mui/icons-material';
import { Navbar } from '../../shared/ui/Navbar';
import { TicketCard, AddTicketCard } from '../../features/tickets/ui/TicketCard';
import { AutoGenerateModal } from '../../features/tickets/ui/AutoGenerateModal';
import { QuestionSelectScreen } from '../../features/tickets/ui/QuestionSelectScreen';
import { DeleteGroupDialog } from '../../features/students/ui/DeleteGroupDialog';
import { useTickets } from '../../features/tickets/model/useTickets';
import { storage } from '../../shared/lib/storage';

export const TicketsPage = () => {
    const {
        tickets, autoMode, handleAutoToggle,
        autoModalOpen, setAutoModalOpen, autoCount, setAutoCount, handleAutoGenerate,
        questionSelectOpen, editingTicket,
        selectedQuestionIds, toggleQuestion, saveTicket, cancelSelect, openCreate, openEdit,
        deleteTarget, askDelete, cancelDelete, confirmDelete, getManualLimit, handleAutoModalClose
    } = useTickets();

    const questions = storage.get('questions_data')?.questions ?? [];

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#5E83AE' }}>
            <Navbar activePath="/tickets" />

            <Box sx={{ px: 4, py: 15 }}>
                {questionSelectOpen ? (
                    <QuestionSelectScreen
                        questions={questions}
                        selectedIds={selectedQuestionIds}
                        onToggle={toggleQuestion}
                        onSave={saveTicket}
                        onCancel={cancelSelect}
                        editingTicket={editingTicket}
                        limit={getManualLimit()}
                    />
                ) : (
                    <>
                        <Box
                            onClick={handleAutoToggle}
                            sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3, cursor: 'pointer', width: 'fit-content' }}
                        >
                            <Box sx={{
                                width: 26,
                                height: 26,
                                border: '1.5px solid #F9F5ED',
                                borderRadius: '6px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                backgroundColor: autoMode ? '#F9F5ED' : 'transparent',
                            }}>
                                {autoMode && <CheckIcon sx={{ fontSize: 18, color: '#2A2A2A' }} />}
                            </Box>
                            <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1.2rem' }}>
                                Автоматическое добавление
                            </Box>
                        </Box>

                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                            <AddTicketCard onClick={openCreate} />
                            {tickets.map((t) => (
                                <TicketCard
                                    key={t.id}
                                    ticket={t}
                                    onEdit={openEdit}
                                    onDelete={askDelete}
                                />
                            ))}
                        </Box>
                    </>
                )}
            </Box>

            <AutoGenerateModal
                open={autoModalOpen}
                onClose={handleAutoModalClose}
                value={autoCount}
                onChange={setAutoCount}
                onSave={handleAutoGenerate}
            />

            <DeleteGroupDialog
                open={!!deleteTarget}
                onConfirm={confirmDelete}
                onCancel={cancelDelete}
                message="Удалить билет?"
            />
        </Box>
    );
};