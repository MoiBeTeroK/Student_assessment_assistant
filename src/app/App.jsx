import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from './theme';
import { LoginPage } from '../pages/login';

export const App = () => {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <LoginPage />
        </ThemeProvider>
    );
};
