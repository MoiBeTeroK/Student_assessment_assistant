import { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import { Check as CheckIcon } from '@mui/icons-material';
import { Navbar } from '../../shared/ui/Navbar';
import { TicketCard, AddTicketCard } from '../../features/tickets/ui/TicketCard';
import { AutoGenerateModal } from '../../features/tickets/ui/AutoGenerateModal';
import { QuestionSelectScreen } from '../../features/tickets/ui/QuestionSelectScreen';
import { DeleteGroupDialog } from '../../features/students/ui/DeleteGroupDialog';
import { useTickets } from '../../features/tickets/model/useTickets';

const btnSx = {
    fontFamily: '"Montserrat", sans-serif',
    fontWeight: '400',
    backgroundColor: '#F9F5ED',
    borderColor: '#2A2A2A',
    color: '#2A2A2A',
    borderRadius: '20px',
    textTransform: 'none',
    fontSize: '1.2rem',
    '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#F9F5ED' },
};

export const TicketsPage = () => {
    const [exportAnchor, setExportAnchor] = useState(null);

    const {
        tickets, questions, disciplineId,
        allQuestionsHaveScore,
        autoMode, handleAutoToggle,
        autoModalOpen, handleAutoModalClose, autoCount, setAutoCount, handleAutoGenerate,
        questionSelectOpen, editingTicket,
        selectedQuestionIds, toggleQuestion, saveTicket, cancelSelect, openCreate, openEdit,
        deleteTarget, askDelete, cancelDelete, confirmDelete,
        getManualLimit, getEffectiveLimit, exportTickets,
    } = useTickets();

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
                        limit={getEffectiveLimit()}
                    />
                ) : (
                    <>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 3, mb: 3, flexWrap: 'wrap' }}>
                            {/* Чекбокс автоматического добавления */}
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                                <Box
                                    onClick={handleAutoToggle}
                                    sx={{
                                        display: 'flex', alignItems: 'center', gap: 1.5,
                                        cursor: allQuestionsHaveScore ? 'pointer' : 'not-allowed',
                                        width: 'fit-content',
                                        opacity: allQuestionsHaveScore ? 1 : 0.5,
                                    }}
                                >
                                    <Box sx={{
                                        width: 26, height: 26,
                                        border: '1.5px solid #F9F5ED',
                                        borderRadius: '6px',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        backgroundColor: autoMode ? '#F9F5ED' : 'transparent',
                                    }}>
                                        {autoMode && <CheckIcon sx={{ fontSize: 18, color: '#2A2A2A' }} />}
                                    </Box>
                                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1.2rem' }}>
                                        Автоматическое добавление
                                    </Box>
                                </Box>
                                {!allQuestionsHaveScore && (
                                    <Box sx={{
                                        fontFamily: '"Montserrat", sans-serif',
                                        color: 'rgba(249,245,237,0.7)',
                                        fontSize: '0.85rem',
                                        maxWidth: 380,
                                    }}>
                                        Автоматическое добавление недоступно, введены не все весовые коэффициенты вопросов
                                    </Box>
                                )}
                            </Box>

                            {/* Кнопка экспорта */}
                            <Button
                                variant="outlined"
                                onClick={(e) => setExportAnchor(e.currentTarget)}
                                disabled={!disciplineId || tickets.length === 0}
                                sx={{
                                    ...btnSx,
                                    '&.Mui-disabled': { borderColor: 'rgba(249,245,237,0.3)', color: 'rgba(249,245,237,0.3)', backgroundColor: 'transparent' },
                                }}
                            >
                                Экспорт билетов
                            </Button>
                            <Menu
                                anchorEl={exportAnchor}
                                open={Boolean(exportAnchor)}
                                onClose={() => setExportAnchor(null)}
                            >
                                <MenuItem onClick={() => { exportTickets('docx'); setExportAnchor(null); }}>DOCX</MenuItem>
                                <MenuItem onClick={() => { exportTickets('pdf'); setExportAnchor(null); }}>PDF</MenuItem>
                            </Menu>
                        </Box>

                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                            <AddTicketCard onClick={openCreate} />
                            {[...tickets].sort((a, b) => a.test_number - b.test_number).map((t) => (
                                <TicketCard
                                    key={t.id_test}
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
