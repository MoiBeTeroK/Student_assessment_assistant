import { useState } from 'react';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import { Edit as EditIcon, Delete as DeleteIcon, ExpandMore as ExpandMoreIcon, ExpandLess as ExpandLessIcon } from '@mui/icons-material';

export const QuestionRow = ({ index, question, onEdit, onDelete, weightColumn }) => {
    const [hovered, setHovered] = useState(false);
    const [answerVisible, setAnswerVisible] = useState(false);

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
                        {index}.&nbsp;{question.question_content}
                    </Box>
                    <Box sx={{ display: 'flex', gap: 0.5, opacity: hovered ? 1 : 0, transition: 'opacity 0.15s ease' }}>
                        {onEdit && (
                            <IconButton size="small" onClick={() => onEdit(question)} sx={{ p: 0.3 }}>
                                <EditIcon sx={{ fontSize: 18, color: '#F9F5ED' }} />
                            </IconButton>
                        )}
                        <IconButton size="small" onClick={() => onDelete(question.id_question ?? question._tempId)} sx={{ p: 0.3 }}>
                            <DeleteIcon sx={{ fontSize: 18, color: '#F9F5ED' }} />
                        </IconButton>
                    </Box>
                </Box>

                {question.complexity_score != null && !weightColumn && (
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1rem', pl: 2 }}>
                        Коэффициент: {question.complexity_score}
                    </Box>
                )}

                {question.standard_answer && (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Box
                            sx={{ display: 'flex', alignItems: 'center', gap: 0.5, cursor: 'pointer', width: 'fit-content' }}
                            onClick={() => setAnswerVisible((v) => !v)}
                        >
                            <IconButton size="small" sx={{ p: 0 }}>
                                {answerVisible
                                    ? <ExpandLessIcon sx={{ fontSize: 18, color: 'rgba(249,245,237,0.7)' }} />
                                    : <ExpandMoreIcon sx={{ fontSize: 18, color: 'rgba(249,245,237,0.7)' }} />
                                }
                            </IconButton>
                            <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: 'rgba(249,245,237,0.7)', fontSize: '0.95rem' }}>
                                Эталонный ответ
                            </Box>
                        </Box>
                        {answerVisible && (
                            <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1rem', pl: 2 }}>
                                {question.standard_answer}
                            </Box>
                        )}
                    </Box>
                )}
            </Box>

            {weightColumn && (
                <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1rem', textAlign: 'center', pt: 0.3 }}>
                    {question.complexity_score ?? '—'}
                </Box>
            )}
        </Box>
    );
};
