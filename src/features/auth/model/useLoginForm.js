import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
const HARDCODED_LOGIN = 'admin'
const HARDCODED_PASSWORD = '123456'

export const useLoginForm = () => {
    const navigate = useNavigate();
    const [login, setLogin] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!login.trim() || !password.trim()) {
            setError('Заполните все поля');
            return;
        }

        setLoading(true);
        try {

            await new Promise((r) => setTimeout(r, 800));
            if (login !== HARDCODED_LOGIN || password !== HARDCODED_PASSWORD) {
                setError('Неверный логин или пароль');
                return;
            }
            navigate('/settings');

            console.log('Login:', { login, password });
        } catch {
            setError('Неверный логин или пароль');
        } finally {
            setLoading(false);
        }
    };

    return {
        login,
        setLogin,
        password,
        setPassword,
        loading,
        error,
        handleSubmit,
    };
};
