import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import { Close as CloseIcon } from '@mui/icons-material';

const inputSx = {
    '& .MuiOutlinedInput-root': {
        borderRadius: '10px',
        '& fieldset': { borderColor: '#5E83AE', borderWidth: 1.5 },
        '&:hover fieldset': { borderColor: '#5E83AE' },
        '&.Mui-focused fieldset': { borderColor: '#5E83AE' },
    },
    '& input': { fontFamily: '"Montserrat", sans-serif', color: '#2A2A2A' },
};

export const AutoGenerateModal = ({ open, onClose, value, onChange, onSave }) => {
    if (!open) return null;

    return (
        <Box sx={{
            position: 'fixed', inset: 0, zIndex: 2000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            backgroundColor: 'rgba(0,0,0,0.4)',
        }}>
            <Box sx={{
                backgroundColor: '#F9F5ED',
                borderRadius: '16px',
                p: 2.5,
                width: 400,
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                position: 'relative',
            }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', fontSize: '1.3rem', color: '#2A2A2A' }}>
                        Генерация билетов
                    </Box>
                    <IconButton size="small" onClick={onClose}>
                        <CloseIcon sx={{ fontSize: 26, color: '#2A2A2A' }} />
                    </IconButton>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', fontSize: '1.2rem', color: '#2A2A2A', whiteSpace: 'nowrap' }}>
                        Количество билетов
                    </Box>
                    <TextField
                        size="small"
                        type="number"
                        value={value}
                        onChange={(e) => {
                            const v = e.target.value;
                            if (v === '' || parseInt(v) > 0) onChange(v);
                        }}
                        sx={{ ...inputSx, width: 120 }}
                    />
                </Box>

                <Button
                    variant="contained"
                    onClick={onSave}
                    disabled={!value || parseInt(value) <= 0}
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
