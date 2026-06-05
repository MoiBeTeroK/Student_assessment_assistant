import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/AuthContext';

export const useLoginForm = () => {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!username.trim() || !password.trim()) {
            setError('Заполните все поля');
            return;
        }

        setLoading(true);
        try {
            await login(username, password);
            navigate('/exam');
        } catch (err) {
            setError(err.message || 'Неверный логин или пароль');
        } finally {
            setLoading(false);
        }
    };

    return { username, setUsername, password, setPassword, loading, error, handleSubmit };
};
