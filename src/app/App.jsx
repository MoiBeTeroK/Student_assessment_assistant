import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { AuthProvider, useAuth } from './AuthContext';
import { theme } from './theme';
import { LoginPage } from '../pages/login';
import { ExamPage } from '../pages/exam';
import { QuestionsPage } from '../pages/questions';
import { SettingsPage } from '../pages/settings';
import { StudentsPage } from '../pages/students';
import { TicketsPage } from '../pages/tickets';

const ProtectedRoute = ({ children }) => {
    const { accessToken, initializing } = useAuth();
    if (initializing) return null;
    if (!accessToken) return <Navigate to="/login" replace />;
    return children;
};

const AppRoutes = () => {
    const { accessToken, initializing } = useAuth();
    if (initializing) return null;

    return (
        <Routes>
            <Route
                path="/login"
                element={accessToken ? <Navigate to="/exam" replace /> : <LoginPage />}
            />
            <Route path="/students" element={<ProtectedRoute><StudentsPage /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
            <Route path="/questions" element={<ProtectedRoute><QuestionsPage /></ProtectedRoute>} />
            <Route path="/tickets" element={<ProtectedRoute><TicketsPage /></ProtectedRoute>} />
            <Route path="/exam" element={<ProtectedRoute><ExamPage /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
    );
};

export const App = () => {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <BrowserRouter>
                <AuthProvider>
                    <AppRoutes />
                </AuthProvider>
            </BrowserRouter>
        </ThemeProvider>
    );
};
