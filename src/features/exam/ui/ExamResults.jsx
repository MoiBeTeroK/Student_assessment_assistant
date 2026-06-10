import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';


const textSx = { fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED' };

const inputSx = {
    '& .MuiOutlinedInput-root': {
        backgroundColor: '#F9F5ED',
        borderRadius: '10px',
        width: 50,
        '& fieldset': { borderColor: '#2A2A2A'},
        '&.Mui-focused fieldset': { borderColor: '#2A2A2A' },
    },
    '& input': { fontFamily: '"Montserrat", sans-serif', color: '#5E83AE', textAlign: 'center' },
    '&:hover': { borderColor: '#5E83AE' },
};

export const ExamResults = ({ recommendedGrade, gradeComment, finalGrade, setFinalGrade, onSave, generatingComment }) => {
    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 700 }}>
            <Box>
                <Box sx={{ ...textSx, fontSize: '1.2rem', mb: 0.5 }}>Рекомендуемая оценка:</Box>
                <Box sx={{ ...textSx, fontSize: '1.1rem' }}>{recommendedGrade}</Box>
            </Box>

            <Box>
                <Box sx={{ ...textSx, fontSize: '1.2rem', mb: 0.5 }}>Комментарий к рекомендуемой оценке:</Box>
                {generatingComment
                    ? <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CircularProgress size={16} sx={{ color: '#F9F5ED' }} />
                        <Box sx={{ ...textSx, fontSize: '1rem' }}>Генерирую...</Box>
                      </Box>
                    : gradeComment && (
                        <Box sx={{ ...textSx, fontSize: '1rem', lineHeight: 1.6, whiteSpace: 'pre-line' }}>{gradeComment}</Box>
                    )
                }
            </Box>

            <Box>
                <Box sx={{ ...textSx, fontSize: '1.2rem', mb: 1 }}>Итоговая оценка студента:</Box>
                <TextField
                    value={finalGrade}
                    onChange={(e) => {
                        const v = e.target.value;
                        if (v === '' || ['2', '3', '4', '5'].includes(v)) setFinalGrade(v ? parseInt(v) : '');
                    }}
                    type="text"
                    size="small"
                    inputProps={{ maxLength: 1 }}
                    sx={inputSx}
                />
            </Box>

            <Button
                variant="outlined"
                onClick={onSave}
                disabled={!finalGrade}
                sx={{
                    fontFamily: '"Montserrat", sans-serif',
                    backgroundColor: finalGrade ? '#F9F5ED' : 'transparent',
                    borderColor: finalGrade ? '#2A2A2A' : 'rgba(249,245,237,0.4)',
                    color: finalGrade ? '#2A2A2A' : 'rgba(249,245,237,0.4)',
                    borderRadius: '20px',
                    textTransform: 'none',
                    fontSize: '1rem',
                    width: 'fit-content',
                    '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#F9F5ED' },
                    '&.Mui-disabled': { borderColor: 'rgba(249,245,237,0.3)', color: 'rgba(249,245,237,0.3)' },
                }}
            >
                Сохранить результаты экзамена
            </Button>
        </Box>
    );
};