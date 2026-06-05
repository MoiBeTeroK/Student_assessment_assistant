import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { Add as AddIcon } from '@mui/icons-material';
import { DisciplineCard } from './DisciplineCard';
import { useSettings } from '../model/useSettings';

export const SettingsForm = ({currentUser}) => {
    const {
        manualCount,
        handleManualCount,
        autoCount,
        handleAutoCount,
        disciplines,
        addDiscipline,
        editDiscipline,
        deleteDiscipline,
        logout,
        toggleActive,
    } = useSettings(currentUser);

    const labelSx = {
        fontSize: '1.2rem',
        color: '#F9F5ED',
        mb: 0.5,
    };

    const inputSx = {
        '& .MuiOutlinedInput-root': {
            backgroundColor: '#F9F5ED',
            borderRadius: '8px',
            '& fieldset': { borderColor: '#2A2A2A', borderWidth: 1.5 },
            '&:hover fieldset': { borderColor: '#2A2A2A' },
            '&.Mui-focused fieldset': { borderColor: '#2A2A2A', borderWidth: 1.5 },
        },
        '& input': {
            fontFamily: '"Montserrat", sans-serif',
            color: '#2A2A2A',
            padding: '10px 14px',
        },
    };

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box>
                <Typography sx={labelSx}>
                    Количество вопросов в билете при ручном создании
                </Typography>
                <TextField
                    value={manualCount}
                    onChange={(e) => handleManualCount(e)}
                    type="number"
                    size="small"
                    sx={{ ...inputSx, width: 280 }}
                />
            </Box>

            <Box>
                <Typography sx={labelSx}>
                    Количество вопросов в билете при автоматическом создании
                </Typography>
                <TextField
                    value={autoCount}
                    onChange={(e) => handleAutoCount(e)}
                    type="number"
                    size="small"
                    sx={{ ...inputSx, width: 280 }}
                />
            </Box>

            <Box>
                <Typography sx={labelSx}>Управление дисциплинами</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mt: 0.5 }}>
                    <Box
                        onClick={addDiscipline}
                        sx={{
                            color: '#2A2A2A',
                            borderColor: '#2A2A2A',
                            backgroundColor: '#F9F5ED',
                            border: '1.5px solid',
                            borderRadius: '10px',
                            width: 220,
                            minHeight: 120,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexDirection: 'row',
                            gap: 2,
                            cursor: 'pointer',
                            '&:hover': {
                                backgroundColor: 'rgba(249,245,237,0.5)',
                                borderColor: '#F9F5ED',
                            },
                        }}
                    >
                        <AddIcon sx={{ color: '#2A2A2A', fontSize: 28 }} />
                        <Typography
                            sx={{
                                fontFamily: '"Montserrat", sans-serif',
                                color: '#2A2A2A',
                                fontSize: '1.2rem',
                                maxWidth: 120,
                            }}
                        >
                            Добавить дисциплину
                        </Typography>
                    </Box>

                    {disciplines.map((d) => (
                        <DisciplineCard
                            key={d.id}
                            discipline={d}
                            onEdit={editDiscipline}
                            onDelete={deleteDiscipline}
                            onToggleActive={toggleActive}
                        />
                    ))}
                </Box>
            </Box>

            <Box sx={{ mt: 2 }}>
                <Button
                    variant="outlined"
                    onClick={logout}
                    sx={{
                        fontFamily: '"Montserrat", sans-serif',
                        fontSize: '1.2rem',
                        fontWeight: 400,
                        color: '#2A2A2A',
                        borderColor: '#2A2A2A',
                        backgroundColor: '#F9F5ED',
                        borderRadius: '20px',
                        textTransform: 'none',
                        px: 3,
                        py: 1,
                        '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#F9F5ED' },
                    }}
                >
                    Выйти из аккаунта
                </Button>
            </Box>
        </Box>
    );
};