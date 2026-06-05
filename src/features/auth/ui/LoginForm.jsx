import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import { useLoginForm } from '../model/useLoginForm';

export const LoginForm = () => {
    const { username, setUsername, password, setPassword, loading, error, handleSubmit } = useLoginForm();

    return (
        <Box
            component="form"
            onSubmit={handleSubmit}
            noValidate
            sx={{ display: 'flex', flexDirection: 'column', gap: '24px' }}
        >
            {error && (
                <Alert
                    severity="error"
                    sx={{
                        borderRadius: '10px',
                        backgroundColor: '#fdecea',
                        color: '#2A2A2A',
                        border: '1.5px solid #c0392b',
                    }}
                >
                    {error}
                </Alert>
            )}

            <Box>
                <Box
                    component="label"
                    htmlFor="login-input"
                    sx={{
                        display: 'block',
                        fontSize: '1.35rem',
                        color: '#2A2A2A',
                        marginBottom: '4px',
                    }}
                >
                    Логин
                </Box>
                <TextField
                    id="login-input"
                    fullWidth
                    variant="outlined"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    autoComplete="username"
                    InputLabelProps={{ shrink: false }}
                    label=""
                />
            </Box>

            <Box>
                <Box
                    component="label"
                    htmlFor="password-input"
                    sx={{
                        display: 'block',
                        fontSize: '1.35rem',
                        color: '#2A2A2A',
                        marginBottom: '4px',
                    }}
                >
                    Пароль
                </Box>
                <TextField
                    id="password-input"
                    fullWidth
                    variant="outlined"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
                    InputLabelProps={{ shrink: false }}
                    label=""
                />
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'center', mt: '8px' }}>
                <Button
                    type="submit"
                    variant="outlined"
                    disabled={loading}
                    sx={{
                        fontSize: '1.35rem',
                        color: '#2A2A2A',
                        borderColor: '#2A2A2A',
                        borderWidth: 1.5,
                        borderRadius: '10px',
                        paddingX: '56px',
                        paddingY: '12px',
                        textTransform: 'none',
                        backgroundColor: 'transparent',
                        minWidth: '200px',
                        '&:hover': {
                            backgroundColor: 'rgba(0,0,0,0.04)',
                            borderColor: '#333',
                            borderWidth: 1.5,
                        },
                    }}
                >
                    {loading ? <CircularProgress size={22} sx={{ color: '#2A2A2A' }} /> : 'Войти'}
                </Button>
            </Box>
        </Box>
    );
};
