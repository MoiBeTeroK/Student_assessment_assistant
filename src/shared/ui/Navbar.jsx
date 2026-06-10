import { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Drawer from '@mui/material/Drawer';
import { Menu as MenuIcon, Close as CloseIcon } from '@mui/icons-material';
import { useMediaQuery } from '@mui/material';

const NAV_ITEMS = [
    { label: 'Экзамен', path: '/exam' },
    { label: 'Список вопросов', path: '/questions' },
    { label: 'Билеты', path: '/tickets' },
    { label: 'Список студентов', path: '/students' },
    { label: 'Итоги экзамена', path: '/exam-results' },
];

const btnSx = (active) => ({
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
    backgroundColor: active ? 'rgba(94,131,174,0.2)' : 'transparent',
    '&:hover': { backgroundColor: 'rgba(94,131,174,0.2)', borderColor: '#5E83AE' },
});

export const Navbar = ({ activePath }) => {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const isMobile = useMediaQuery('(max-width:768px)');

    return (
        <Box
            component="nav"
            sx={{
                position: 'fixed',
                top: 0, left: 0, right: 0,
                zIndex: 1000,
                backgroundColor: '#F9F5ED',
                px: 3,
                py: 1.5,
                display: 'flex',
                alignItems: 'center',
                gap: 2,
            }}
        >
            {isMobile ? (
                <>
                    <IconButton onClick={() => setDrawerOpen(true)} sx={{ color: '#2A2A2A' }}>
                        <MenuIcon />
                    </IconButton>

                    <Drawer
                        anchor="left"
                        open={drawerOpen}
                        onClose={() => setDrawerOpen(false)}
                        PaperProps={{ sx: { backgroundColor: '#F9F5ED', width: 240, p: 2 } }}
                    >
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                            <IconButton onClick={() => setDrawerOpen(false)} sx={{ color: '#2A2A2A' }}>
                                <CloseIcon />
                            </IconButton>
                        </Box>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, alignItems: 'center' }}>
                            {[...NAV_ITEMS, { label: 'Настройки', path: '/settings' }].map((item) => (
                                <Button
                                    key={item.path}
                                    variant="outlined"
                                    href={item.path}
                                    onClick={() => setDrawerOpen(false)}
                                    sx={{
                                        ...btnSx(activePath === item.path),
                                        maxWidth: '100%',
                                        width: '100%',
                                        justifyContent: 'center',
                                    }}
                                >
                                    {item.label}
                                </Button>
                            ))}
                        </Box>
                    </Drawer>
                </>
            ) : (
                <>
                    <Box sx={{ display: 'flex', gap: 3, flex: 1 }}>
                        {NAV_ITEMS.map((item) => (
                            <Button
                                key={item.path}
                                variant="outlined"
                                href={item.path}
                                sx={btnSx(activePath === item.path)}
                            >
                                {item.label}
                            </Button>
                        ))}
                    </Box>
                    <Button
                        variant="outlined"
                        href="/settings"
                        sx={{ ...btnSx(activePath === '/settings'), maxWidth: 'none' }}
                    >
                        Настройки
                    </Button>
                </>
            )}
        </Box>
    );
};
