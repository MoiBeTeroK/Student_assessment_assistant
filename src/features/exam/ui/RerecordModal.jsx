import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import { Close as CloseIcon } from '@mui/icons-material';

export const RerecordModal = ({ open, passphrase, onChange, onConfirm, onClose }) => {
    if (!open) return null;

    const inputSx = {
        '& .MuiOutlinedInput-root': {
            borderRadius: '10px',
            '& fieldset': { borderColor: '#5E83AE' },
            '&.Mui-focused fieldset': { borderColor: '#5E83AE' },
        },
        '& input': { fontFamily: '"Montserrat", sans-serif', color: '#5E83AE' },
        '&:hover': { borderColor: '#5E83AE' },
    };

    return (
        <Box sx={{
            position: 'fixed', inset: 0, zIndex: 2000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            backgroundColor: 'rgba(0,0,0,0.4)',
        }}>
            <Box sx={{
                backgroundColor: '#F9F5ED',
                borderRadius: '20px',
                p: 2,
                width: 360,
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
            }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', fontSize: '1.2rem', color: '#2A2A2A' }}>
                        Введите кодовую фразу
                    </Box>
                    <IconButton size="small" onClick={onClose}>
                        <CloseIcon sx={{ fontSize: 24, color: '#2A2A2A' }} />
                    </IconButton>
                </Box>

                <TextField
                    fullWidth
                    size="small"
                    type="password"
                    value={passphrase}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder="Кодовая фраза"
                    sx={inputSx}
                />

                <Button
                    variant="outlined"
                    onClick={onConfirm}
                    disabled={!passphrase}
                    sx={{
                        fontFamily: '"Montserrat", sans-serif',
                        fontWeight: '400',
                        textTransform: 'none',
                        backgroundColor: '#F9F5ED',
                        borderColor: '#2A2A2A',
                        color: '#2A2A2A',
                        borderRadius: '20px',
                        fontSize: '1.2rem',
                        width: 'fit-content',
                        alignSelf: 'center',
                        px: 4,
                        '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#5E83AE' },
                        '&.Mui-disabled': {
                            borderColor: 'rgba(42,42,42,0.4)',
                            color: 'rgba(42,42,42,0.4)',
                            backgroundColor: 'transparent',
                        },
                    }}
                >
                    Подтвердить
                </Button>
            </Box>
        </Box>
    );
};