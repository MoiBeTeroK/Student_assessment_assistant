import Box from '@mui/material/Box';
import Button from '@mui/material/Button';

export const DeleteGroupDialog = ({ open, onConfirm, onCancel }) => {
    if (!open) return null;

    return (
        <Box sx={{
            position: 'fixed', inset: 0, zIndex: 2000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            backgroundColor: 'rgba(0,0,0,0.4)',
        }}>
            <Box sx={{
                backgroundColor: '#F9F5ED',
                borderRadius: '30px',
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 3,
                minWidth: '400px',
                maxHeight: '150px',
            }}>
                <Box sx={{ fontFamily: '"Montserrat", sans-serif', fontSize: '1.4rem', color: '#2A2A2A' }}>
                    Удалить группу?
                </Box>
                <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                        variant="contained"
                        onClick={onConfirm}
                        sx={{
                            fontFamily: '"Montserrat", sans-serif',
                            backgroundColor: '#5E83AE',
                            borderRadius: '10px',
                            fontSize: '1.1rem',
                            textTransform: 'none',
                            boxShadow: 'none',
                            px: 3,
                            '&:hover': { backgroundColor: '#57799f', boxShadow: 'none', },
                        }}
                    >
                        Удалить
                    </Button>
                    <Button
                        variant="contained"
                        onClick={onCancel}
                        sx={{
                            fontFamily: '"Montserrat", sans-serif',
                            backgroundColor: '#5E83AE',
                            borderRadius: '10px',
                            fontSize: '1.1rem',
                            textTransform: 'none',
                            boxShadow: 'none',
                            px: 3,
                            '&:hover': { backgroundColor: '#57799f', boxShadow: 'none', },
                        }}
                    >
                        Отмена
                    </Button>
                </Box>
            </Box>
        </Box>
    );
};