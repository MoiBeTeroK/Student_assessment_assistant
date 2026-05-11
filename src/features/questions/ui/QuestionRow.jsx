import { useState } from 'react';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';

export const QuestionRow = ({ index, question, onEdit, onDelete, weightColumn }) => {
    const [hovered, setHovered] = useState(false);

    return (
        <Box
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            sx={{
                display: 'grid',
                gridTemplateColumns: weightColumn ? '1fr 160px' : '1fr',
                alignItems: 'flex-start',
                py: 1.5,
                borderBottom: '1px solid rgba(249,245,237,0.15)',
            }}
        >
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1.2rem' }}>
                        {index}.&nbsp;{question.name}
                    </Box>
                    <Box sx={{ display: 'flex', gap: 0.5, opacity: hovered ? 1 : 0, transition: 'opacity 0.15s ease' }}>
                        {onEdit && (
                            <IconButton size="small" onClick={() => onEdit(question)} sx={{ p: 0.3 }}>
                                <EditIcon sx={{ fontSize: 18, color: '#F9F5ED' }} />
                            </IconButton>
                        )}
                        <IconButton size="small" onClick={() => onDelete(question.id)} sx={{ p: 0.3 }}>
                            <DeleteIcon sx={{ fontSize: 18, color: '#F9F5ED' }} />
                        </IconButton>
                    </Box>
                </Box>

                {question.weight && !weightColumn && (
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1rem', pl: 2 }}>
                        Коэффициент: {question.weight}
                    </Box>
                )}

                {question.referenceAnswer && (
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1rem', pl: 2 }}>
                        Эталонный ответ: {question.referenceAnswer}
                    </Box>
                )}
            </Box>

            {weightColumn && (
                <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1rem', textAlign: 'center', pt: 0.3 }}>
                    {question.weight ?? '—'}
                </Box>
            )}
        </Box>
    );
};