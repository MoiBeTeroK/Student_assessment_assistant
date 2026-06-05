import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import { LoginForm } from '../../features/auth/ui/LoginForm';

export const LoginPage = () => {
    return (
        <Box
            sx={{
                minHeight: '100vh',
                backgroundColor: '#5E83AE',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
            }}
        >
            <Paper
                elevation={0}
                sx={{
                    backgroundColor: '#F9F5ED',
                    borderRadius: '30px',
                    padding: '32px 30px 54px',
                    width: '100%',
                    maxWidth: '460px',
                    mx: 2,
                }}
            >
                <Typography
                    component="h1"
                    sx={{
                        fontSize: '2.2rem',
                        fontWeight: 400,
                        color: '#2A2A2A',
                        textAlign: 'center',
                        marginBottom: '32px',
                    }}
                >
                    Вход
                </Typography>

                <LoginForm />
            </Paper>
        </Box>
    );
};
