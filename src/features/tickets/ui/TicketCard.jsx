import { useState } from 'react';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import {Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon} from '@mui/icons-material';

const cardSx = {
    backgroundColor: '#F9F5ED',
    borderRadius: '20px',
    border: '1.5px solid #2A2A2A',
    width: 220,
    height: 120,
    display: 'flex',
    flexDirection: 'column',
    gap: 1,
    p: 1,
    cursor: 'pointer',
    position: 'relative',
};

export const TicketCard = ({ ticket, onEdit, onDelete }) => {
    const [hovered, setHovered] = useState(false);

    return (
        <Box
            sx={cardSx}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
        >
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 0.5}}>
                <IconButton size="small" onClick={(e) => { e.stopPropagation(); onEdit(ticket); }} sx={{ p: 0.3 }}>
                    <EditIcon sx={{ fontSize: 24, color: '#2A2A2A' }} />
                </IconButton>
                <IconButton size="small" onClick={(e) => { e.stopPropagation(); onDelete(ticket.id_test); }} sx={{ p: 0.3 }}>
                    <DeleteIcon sx={{ fontSize: 24, color: '#2A2A2A' }} />
                </IconButton>
            </Box>
            <Box sx={{ fontFamily: '"Montserrat", sans-serif', fontSize: '1.4rem', color: '#2A2A2A' , display: 'flex', justifyContent: 'center' }}>
                Билет №{ticket.test_number}
            </Box>
        </Box>
    );
};

export const AddTicketCard = ({ onClick }) => (
    <Box
        sx={{ ...cardSx, alignItems: 'center', justifyContent: 'center' }}
        onClick={onClick}
    >
        <AddIcon sx={{ color: '#2A2A2A', fontSize: 34 }} />
    </Box>
);