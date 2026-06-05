import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
    palette: {
        mode: 'light',
        background: {
            default: '#5E83AE',
        },
        text: {
            primary: '#2A2A2A',
            secondary: '#555555',
        },
    },
    typography: {
        fontFamily: '"Montserrat", sans-serif',
    },
    shape: {
        borderRadius: 12,
    },
    components: {
        MuiCssBaseline: {
            styleOverrides: {
                body: {
                    backgroundColor: '#5E83AE',
                    minHeight: '100vh',
                    fontFamily: '"Montserrat", sans-serif',
                },
            },
        },
        MuiOutlinedInput: {
            styleOverrides: {
                root: {
                    backgroundColor: '#F9F5ED',
                    borderRadius: 10,
                    '& fieldset': {
                        borderColor: '#2A2A2A',
                        borderWidth: 1.5,
                    },
                    '&:hover fieldset': {
                        borderColor: '#2A2A2A',
                    },
                    '&.Mui-focused fieldset': {
                        borderColor: '#2A2A2A',
                        borderWidth: 1.5,
                    },
                },
                input: {
                    padding: '14px 16px',
                    fontSize: '1rem',
                    color: '#2A2A2A',
                },
            },
        },
        MuiInputLabel: {
            styleOverrides: {
                root: {
                    color: '#555555',
                    fontSize: '1.1rem',
                    fontFamily: '"Montserrat", sans-serif',
                    '&.Mui-focused': {
                        color: '#2A2A2A',
                    },
                },
            },
        },
    },
});
