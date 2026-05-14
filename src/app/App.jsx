import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from './theme';
import { LoginPage } from '../pages/login';
import { SettingsPage } from '../pages/settings';
import { StudentsPage } from '../pages/students';
import { QuestionsPage } from '../pages/questions';
import { TicketsPage } from '../pages/tickets';
import { ExamPage } from '../pages/exam';

export const App = () => {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/students" element={<StudentsPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                    <Route path="/questions" element={<QuestionsPage />} />
                    <Route path="/tickets" element={<TicketsPage />} />
                    <Route path="/exam" element={<ExamPage />} />
                    <Route path="*" element={<Navigate to="/login" replace />} />
                </Routes>
            </BrowserRouter>
        </ThemeProvider>
    );
};