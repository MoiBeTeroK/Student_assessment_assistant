import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import { Edit as EditIcon, Delete as DeleteIcon, Check as CheckIcon } from '@mui/icons-material';

export const DisciplineCard = ({ discipline, onEdit, onDelete, onToggleActive }) => {
    return (
        <Box
            sx={{
                backgroundColor: '#F9F5ED',
                borderRadius: '10px',
                border: discipline.active ? '2.5px solid #2A2A2A' : '1.5px solid #2A2A2A',
                p: 1.5,
                width: 220,
                minHeight: 120,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
            }}
        >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box
                    onClick={() => onToggleActive(discipline.id)}
                    sx={{
                        width: 22,
                        height: 22,
                        border: '1.5px solid #2A2A2A',
                        borderRadius: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        backgroundColor: discipline.active ? '#2A2A2A' : 'transparent',
                        flexShrink: 0,
                    }}
                >
                    {discipline.active && (
                        <CheckIcon sx={{ fontSize: 16, color: '#F9F5ED' }} />
                    )}
                </Box>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <IconButton size="small" onClick={() => onEdit(discipline.id)} sx={{ p: 0.3 }}>
                        <EditIcon sx={{ fontSize: 20, color: '#2A2A2A' }} />
                    </IconButton>
                    <IconButton size="small" onClick={() => onDelete(discipline.id)} sx={{ p: 0.3 }}>
                        <DeleteIcon sx={{ fontSize: 20, color: '#2A2A2A' }} />
                    </IconButton>
                </Box>
            </Box>

            <Box
                sx={{
                    fontFamily: '"Montserrat", sans-serif',
                    fontSize: '1.2rem',
                    color: '#2A2A2A',
                    mt: 1,
                    lineHeight: 1.4,
                    overflow: 'hidden',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                }}
            >
                {discipline.name}
            </Box>
        </Box>
    );
};