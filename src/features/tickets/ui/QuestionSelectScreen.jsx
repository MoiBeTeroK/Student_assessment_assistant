import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { Check as CheckIcon } from '@mui/icons-material';

const checkboxSx = (checked, disabled) => ({
    width: 26,
    height: 26,
    border: '1.5px solid #F9F5ED',
    borderRadius: '6px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: disabled ? 'not-allowed' : 'pointer',
    flexShrink: 0,
    backgroundColor: checked ? '#F9F5ED' : 'transparent',
    opacity: disabled ? 0.4 : 1,
    transition: 'opacity 0.15s ease',
});

const btnSx = {
    fontFamily: '"Montserrat", sans-serif',
    fontWeight: '400',
    backgroundColor: '#F9F5ED',
    borderColor: '#2A2A2A',
    color: '#2A2A2A',
    fontSize: '1.2rem',
    borderRadius: '20px',
    textTransform: 'none',
    '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#F9F5ED' },
};

export const QuestionSelectScreen = ({ questions, selectedIds, onToggle, onSave, onCancel, editingTicket, limit }) => {
    const limitReached = selectedIds.length >= limit;

    return (
        <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1.2rem' }}>
                    {editingTicket ? editingTicket.name : 'Выбор вопросов для создания билета'}
                </Box>
                <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button variant="outlined" onClick={onSave} sx={btnSx}>
                        Сохранить
                    </Button>
                    <Button
                        variant="outlined"
                        onClick={onCancel}
                        sx={{ ...btnSx }}
                    >
                        Отмена
                    </Button>
                </Box>
            </Box>

            {limit !== Infinity && (
                <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: 'rgba(249,245,237,0.7)', fontSize: '0.85rem', mb: 2 }}>
                    Выбрано {selectedIds.length} из {limit} вопросов
                </Box>
            )}

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {questions.length === 0 && (
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: 'rgba(249,245,237,0.7)', fontSize: '1.2rem' }}>
                        Нет доступных вопросов. Сначала добавьте вопросы в разделе «Список вопросов».
                    </Box>
                )}
                {questions.map((q) => {
                    const checked = selectedIds.includes(q.id);
                    const disabled = !checked && limitReached;
                    return (
                        <Box
                            key={q.id}
                            onClick={() => !disabled && onToggle(q.id)}
                            sx={{ display: 'flex', alignItems: 'center', gap: 2, cursor: disabled ? 'not-allowed' : 'pointer' }}
                        >
                            <Box sx={checkboxSx(checked, disabled)}>
                                {checked && <CheckIcon sx={{ fontSize: 20, color: '#2A2A2A' }} />}
                            </Box>
                            <Box sx={{
                                fontFamily: '"Montserrat", sans-serif',
                                color: disabled ? 'rgba(249,245,237,0.4)' : '#F9F5ED',
                                fontSize: '1.2rem',
                            }}>
                                {q.name}
                            </Box>
                        </Box>
                    );
                })}
            </Box>
        </Box>
    );
};