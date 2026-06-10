import Box from '@mui/material/Box';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import { Navbar } from '../../shared/ui/Navbar';
import { useExamResults } from '../../features/exam-results/model/useExamResults';

const cellSx = {
    fontFamily: '"Montserrat", sans-serif',
    color: '#F9F5ED',
    fontSize: '1rem',
    px: 2,
    py: 1,
    textAlign: 'center',
    borderBottom: '1px solid rgba(249,245,237,0.2)',
};

const headSx = {
    ...cellSx,
    fontWeight: 600,
    borderBottom: '2px solid rgba(249,245,237,0.4)',
};

const COLS = ['ФИО', 'Группа', 'Рек. оценка', 'Итог. оценка', 'Время сдачи'];


export const ExamResultsPage = () => {
    const { rows, loading, disciplineId, avgGrade, year, setYear, yearOptions } = useExamResults();

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#5E83AE' }}>
            <Navbar activePath="/exam-results" />

            <Box sx={{ px: { xs: 2, md: 4 }, py: { xs: 10, md: 15 } }}>
                <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1.2rem' }}>
                        Год:
                    </Box>
                    <Select
                        value={year}
                        onChange={(e) => setYear(e.target.value)}
                        size="small"
                        sx={{
                            backgroundColor: '#F9F5ED',
                            borderRadius: '8px',
                            fontFamily: '"Montserrat", sans-serif',
                            color: '#2A2A2A',
                            width: 120,
                            '& .MuiOutlinedInput-notchedOutline': { borderColor: '#2A2A2A' },
                        }}
                    >
                        {yearOptions.map((y) => (
                            <MenuItem key={y} value={y} sx={{ fontFamily: '"Montserrat", sans-serif' }}>
                                {y}
                            </MenuItem>
                        ))}
                    </Select>
                </Box>

                {!disciplineId ? (
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1.2rem', textAlign: 'center' }}>
                        Выберите активную дисциплину в настройках
                    </Box>
                ) : loading ? (
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1.2rem' }}>
                        Загрузка...
                    </Box>
                ) : rows.length === 0 ? (
                    <Box sx={{ fontFamily: '"Montserrat", sans-serif', color: '#F9F5ED', fontSize: '1.2rem', textAlign: 'center' }}>
                        Пока нет студентов, сдавших экзамен в {year} году
                    </Box>
                ) : (
                    <Box>
                        <Box sx={{ overflowX: 'auto' }}>
                        <Box component="table" sx={{ width: '100%', minWidth: 500, borderCollapse: 'collapse' }}>
                            <Box component="thead">
                                <Box component="tr">
                                    {COLS.map((col) => (
                                        <Box component="th" key={col} sx={headSx}>{col}</Box>
                                    ))}
                                </Box>
                            </Box>
                            <Box component="tbody">
                                {rows.map((r) => (
                                    <Box component="tr" key={r.id_result}>
                                        <Box component="td" sx={cellSx}>{r.name}</Box>
                                        <Box component="td" sx={cellSx}>{r.group}</Box>
                                        <Box component="td" sx={cellSx}>{r.rec_grade}</Box>
                                        <Box component="td" sx={cellSx}>{r.final_grade}</Box>
                                        <Box component="td" sx={cellSx}>{r.date}</Box>
                                    </Box>
                                ))}
                            </Box>
                        </Box>
                        </Box>

                        <Box sx={{
                            mt: 3,
                            fontFamily: '"Montserrat", sans-serif',
                            color: '#F9F5ED',
                            fontSize: '1.2rem',
                        }}>
                            Средняя оценка: <b>{avgGrade}</b>
                        </Box>
                    </Box>
                )}
            </Box>
        </Box>
    );
};
