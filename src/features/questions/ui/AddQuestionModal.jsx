import { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import CircularProgress from '@mui/material/CircularProgress';
import { Close as CloseIcon } from '@mui/icons-material';

const inputSx = {
    '& .MuiOutlinedInput-root': {
        borderRadius: '10px',
        '& fieldset': { borderColor: '#ccc' },
        '&:hover fieldset': { borderColor: '#888' },
        '&.Mui-focused fieldset': { borderColor: '#5E83AE' },
    },
    '& input, & textarea': { fontFamily: '"Montserrat", sans-serif', color: '#2A2A2A' },
};

export const AddQuestionModal = ({ open, onClose, onSave, initialData = null, title = 'Добавление вопроса' }) => {
    const [name, setName] = useState(initialData?.name ?? '');
    const [weight, setWeight] = useState(initialData?.weight ?? '');
    const [referenceAnswer, setReferenceAnswer] = useState(initialData?.referenceAnswer ?? '');
    const [loadingAnswer, setLoadingAnswer] = useState(false);

    if (!open) return null;

    const handleSave = () => {
        if (!name.trim()) return;
        onSave({ name: name.trim(), weight: weight || null, referenceAnswer: referenceAnswer.trim() });
    };

    const generateAnswer = async () => {
        setLoadingAnswer(true);
        try {
            // бэк
            await new Promise((r) => setTimeout(r, 1200));
            setReferenceAnswer(`Эталонный ответ на вопрос: "${name}". Здесь будет ответ от бэкенда.`);
        } catch {
            setReferenceAnswer('Ошибка генерации ответа');
        } finally {
            setLoadingAnswer(false);
        }
    };

    return (
        <Box sx={{
            position: 'fixed', inset: 0, zIndex: 2000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            backgroundColor: 'rgba(0,0,0,0.4)',
        }}>
            <Box sx={{
                backgroundColor: '#F9F5ED',
                borderRadius: '30px',
                p: 2.5,
                width: 450,
                maxHeight: '85vh',
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                position: 'relative',
            }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', fontSize: '1.4rem', color: '#2A2A2A' }}>
                        {title}
                    </Box>
                    <IconButton size="small" onClick={onClose}>
                        <CloseIcon sx={{ fontSize: 26, color: '#2A2A2A' }} />
                    </IconButton>
                </Box>

                <Box>
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', fontSize: '1.2rem', color: '#2A2A2A', mb: 0.5 }}>
                        Название вопроса
                    </Box>
                    <TextField
                        fullWidth
                        size="small"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        sx={inputSx}
                    />
                </Box>

                <Box>
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', fontSize: '1.2rem', color: '#2A2A2A', mb: 0.5 }}>
                        Весовой коэффициент вопроса
                    </Box>
                    <TextField
                        fullWidth
                        size="small"
                        type="number"
                        value={weight}
                        onChange={(e) => {
                            const v = e.target.value;
                            if (v === '' || (parseFloat(v) >= 0 && parseFloat(v) <= 1)) setWeight(v);
                        }}
                        inputProps={{ step: 0.1, min: 0.1, max: 1 }}
                        sx={inputSx}
                    />
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Button
                        variant="outlined"
                        onClick={generateAnswer}
                        disabled={loadingAnswer || !name.trim()}
                        sx={{
                            fontFamily: '"Montserrat", sans-serif',
                            textTransform: 'none',
                            borderColor: '#5E83AE',
                            color: '#5E83AE',
                            borderRadius: '20px',
                            fontSize: '1rem',
                            '&:hover': { backgroundColor: 'rgba(91,127,166,0.08)' },
                            '&.Mui-disabled': { borderColor: '#ccc', color: '#ccc' },
                        }}
                    >
                        {loadingAnswer
                            ? <><CircularProgress size={16} sx={{ mr: 1, color: '#5E83AE'}} />Генерация...</>
                            : 'Сгенерировать эталонный ответ'
                        }
                    </Button>

                    {(referenceAnswer || loadingAnswer) && (
                        <TextField
                            fullWidth
                            multiline
                            minRows={3}
                            maxRows={8}
                            value={referenceAnswer}
                            onChange={(e) => setReferenceAnswer(e.target.value)}
                            placeholder="Эталонный ответ..."
                            sx={{
                                ...inputSx,
                                '& textarea': { fontFamily: '"Montserrat", sans-serif', color: '#2A2A2A', fontSize: '1rem', p: 0 },
                            }}
                        />
                    )}
                </Box>

                <Button
                    variant="contained"
                    onClick={handleSave}
                    disabled={!name.trim()}
                    sx={{
                        fontFamily: '"Montserrat", sans-serif',
                        textTransform: 'none',
                        backgroundColor: '#5E83AE',
                        borderRadius: '20px',
                        alignSelf: 'center',
                        px: 4,
                        fontSize: '1rem',
                        '&:hover': { backgroundColor: '#5E83AE' },
                        '&.Mui-disabled': { backgroundColor: '#ccc' },
                    }}
                >
                    Сохранить
                </Button>
            </Box>
        </Box>
    );
};