import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import InputBase from '@mui/material/InputBase';
import { Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { useEffect, useRef } from 'react';

const cardBase = {
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

export const GroupCard = ({ group, onSelect, onEdit, onDelete }) => {
    return (
        <Box sx={cardBase} onClick={() => onSelect(group)}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 0.5 }}>
                <IconButton size="small" onClick={(e) => { e.stopPropagation(); onEdit(group.id_group); }} sx={{ p: 0.3 }}>
                    <EditIcon sx={{ fontSize: 24, color: '#2A2A2A' }} />
                </IconButton>
                <IconButton size="small" onClick={(e) => { e.stopPropagation(); onDelete(group.id_group); }} sx={{ p: 0.3 }}>
                    <DeleteIcon sx={{ fontSize: 24, color: '#2A2A2A' }} />
                </IconButton>
            </Box>
            <Box sx={{ fontFamily: '"Montserrat", sans-serif', fontSize: '1.4rem', color: '#2A2A2A', display: 'flex', justifyContent: 'center' }}>
                {group.group_name}
            </Box>
        </Box>
    );
};

export const AddGroupCard = ({ isAdding, value, onChange, onKeyDown, onBlur, onStartAdd }) => {
    const inputRef = useRef(null);
    useEffect(() => { if (isAdding) inputRef.current?.focus(); }, [isAdding]);

    return (
        <Box
            sx={{ ...cardBase, alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
            onClick={!isAdding ? onStartAdd : undefined}
        >
            {isAdding ? (
                <InputBase
                    inputRef={inputRef}
                    value={value}
                    onChange={onChange}
                    onKeyDown={onKeyDown}
                    placeholder="Название группы"
                    sx={{
                        fontFamily: '"Montserrat", sans-serif',
                        fontSize: '1.2rem',
                        color: '#2A2A2A',
                        width: '100%',
                        px: 1,
                    }}
                />
            ) : (
                <AddIcon sx={{ color: '#2A2A2A', fontSize: 34 }} />
            )}
        </Box>
    );
};
