import Box from '@mui/material/Box';
import Button from '@mui/material/Button';

const NAV_ITEMS = [
    { label: 'Экзамен', path: '/exam' },
    { label: 'Список вопросов', path: '/questions' },
    { label: 'Билеты', path: '/tickets' },
    { label: 'Список студентов', path: '/students' },
];

export const Navbar = ({ activePath }) => {
    return (
        <Box
            component="nav"
            sx={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                zIndex: 1000,
                backgroundColor: '#F9F5ED',
                px: 3,
                py: 1.5,
                display: 'flex',
                alignItems: 'center',
                gap: 2,
            }}
        >
            <Box sx={{ display: 'flex', gap: 3, flex: 1 }}>
                {NAV_ITEMS.map((item) => (
                    <Button
                        key={item.path}
                        variant="outlined"
                        href={item.path}
                        sx={{
                            fontSize: '1.2rem',
                            fontWeight: 400,
                            color: '#2A2A2A',
                            borderColor: '#5E83AE',
                            borderRadius: '20px',
                            textTransform: 'none',
                            px: 2.5,
                            py: 0.8,
                            whiteSpace: 'normal',
                            lineHeight: 1.3,
                            textAlign: 'center',
                            maxWidth: '140px',
                            backgroundColor: activePath === item.path ? 'rgba(94,131,174,0.2)' : 'transparent',
                            '&:hover': {
                                backgroundColor: 'rgba(94,131,174,0.2)',
                                borderColor: '#5E83AE',
                            },
                        }}
                    >
                        {item.label}
                    </Button>
                ))}
            </Box>

            <Button
                variant="outlined"
                href="/settings"
                sx={{
                    fontWeight: 400,
                    fontSize: '1.2rem',
                    color: '#2A2A2A',
                    borderColor: '#5E83AE',
                    borderRadius: '20px',
                    textTransform: 'none',
                    px: 2.5,
                    py: 0.8,
                    backgroundColor: activePath === '/settings' ? 'rgba(94,131,174,0.2)' : 'transparent',
                    '&:hover': {
                        backgroundColor: 'rgba(94,131,174,0.2)',
                        borderColor: '#5E83AE',
                    },
                }}
            >
                Настройки
            </Button>
        </Box>
    );
};