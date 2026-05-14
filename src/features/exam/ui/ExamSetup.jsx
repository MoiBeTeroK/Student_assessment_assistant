import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';

const labelSx = {
    fontFamily: '"Montserrat", sans-serif',
    color: '#F9F5ED',
    fontSize: '1.2rem',
    mb: 0.5,
};

const selectSx = {
    backgroundColor: '#F9F5ED',
    borderRadius: '10px',
    fontFamily: '"Montserrat", sans-serif',
    color: '#2A2A2A',
    '& .MuiOutlinedInput-notchedOutline': { borderColor: '#2A2A2A' },
    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#2A2A2A' },
    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#2A2A2A' },
};

const inputSx = {
    '& .MuiOutlinedInput-root': {
        backgroundColor: '#F9F5ED',
        borderRadius: '10px',
        '& fieldset': { borderColor: '#2A2A2A' },
    },
    '& input': { fontFamily: '"Montserrat", sans-serif', color: '#2A2A2A' },
};

export const ExamSetup = ({ tickets, groups, isStudentDone, selectedGroup, setSelectedGroup, selectedStudent, setSelectedStudent, ticketNumber, setTicketNumber, ticketQuestions, onStart }) => {
    const students = selectedGroup?.students ?? [];
    const ticketExists = tickets.some((t) => t.name === `Билет №${ticketNumber}`);

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, maxWidth: 500 }}>
            <Box>
                <Box sx={labelSx}>Выберите группу</Box>
                <Select
                    value={selectedGroup?.id ?? ''}
                    onChange={(e) => {
                        const g = groups.find((g) => g.id === e.target.value);
                        setSelectedGroup(g);
                        setSelectedStudent(null);
                    }}
                    displayEmpty
                    sx={{ ...selectSx, width: 280 }}
                >
                    <MenuItem value="" disabled>Группа</MenuItem>
                    {groups.map((g) => (
                        <MenuItem key={g.id} value={g.id} sx={{ fontFamily: '"Montserrat", sans-serif' }}>
                            {g.name}
                        </MenuItem>
                    ))}
                </Select>
            </Box>

            {selectedGroup && (
                <Box>
                    <Box sx={labelSx}>Выберите студента</Box>
                    <Select
                        value={selectedStudent?.id ?? ''}
                        onChange={(e) => {
                            const s = students.find((s) => s.id === e.target.value);
                            setSelectedStudent(s);
                        }}
                        displayEmpty
                        sx={{ ...selectSx, maxWidth: 400, width: '100%' }}
                    >
                        <MenuItem value="" disabled>Студент</MenuItem>
                        {students.map((s) => {
                            const done = isStudentDone(s.id);
                            return (
                                <MenuItem
                                    key={s.id}
                                    value={s.id}
                                    disabled={done}
                                    sx={{ fontFamily: '"Montserrat", sans-serif', color: done ? '#aaa' : '#2A2A2A' }}
                                >
                                    {s.name}{done ? ' — уже сдал' : ''}
                                </MenuItem>
                            );
                        })}
                    </Select>
                </Box>
            )}

            {selectedStudent && (
                <Box>
                    <Box sx={labelSx}>Введите номер билета</Box>
                    <TextField
                        value={ticketNumber}
                        onChange={(e) => setTicketNumber(e.target.value)}
                        type="number"
                        size="small"
                        error={!!ticketNumber && !ticketExists}
                        helperText={!!ticketNumber && !ticketExists ? 'Такого билета не существует' : ''}
                        sx={{ ...inputSx, width: 280 }}
                    />
                </Box>
            )}

            {ticketQuestions.length > 0 && (
                <Box>
                    <Box sx={labelSx}>Вопросы в билете:</Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        {ticketQuestions.map((q, i) => (
                            <Box key={q.id} sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1.1rem' }}>
                                {i + 1}. {q.name}
                            </Box>
                        ))}
                    </Box>
                </Box>
            )}

            {ticketQuestions.length > 0 && selectedStudent && (
                <Button
                    variant="outlined"
                    onClick={onStart}
                    sx={{
                        fontFamily: '"Montserrat", sans-serif',
                        fontWeight: '400',
                        backgroundColor: '#F9F5ED',
                        borderColor: '#2A2A2A',
                        color: '#2A2A2A',
                        borderRadius: '20px',
                        textTransform: 'none',
                        fontSize: '1.2rem',
                        width: 'fit-content',
                        '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)', borderColor: '#F9F5ED' },
                    }}
                >
                    Записать экзамен
                </Button>
            )}
        </Box>
    );
};