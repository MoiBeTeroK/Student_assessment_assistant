import { useState } from 'react';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';

export const StudentRow = ({ index, student, onEdit, onDelete }) => {
    const [hovered, setHovered] = useState(false);

    return (
        <Box
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                py: 0.5,
                fontFamily: '"Montserrat", sans-serif',
                color: '#F9F5ED',
                fontSize: '1.2rem',
                listStyle: 'none',
            }}
        >
            <Box sx={{ minWidth: 20, color: '#F9F5ED' }}>{index}.</Box>
            <Box>{student.name}</Box>

            <Box sx={{
                display: 'flex',
                gap: 0.5,
                opacity: hovered ? 1 : 0,
                transition: 'opacity 0.15s ease',
            }}>
                <IconButton size="small" onClick={() => onEdit(student.id)} sx={{ p: 0.3 }}>
                    <EditIcon sx={{ fontSize: 18, color: '#F9F5ED' }} />
                </IconButton>
                <IconButton size="small" onClick={() => onDelete(student.id)} sx={{ p: 0.3 }}>
                    <DeleteIcon sx={{ fontSize: 18, color: '#F9F5ED' }} />
                </IconButton>
            </Box>
        </Box>
    );
};