import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { authApi } from '../shared/api/authApi';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [accessToken, setAccessToken] = useState(null);
    const [user, setUser] = useState(null);
    const [initializing, setInitializing] = useState(true);

    // При загрузке страницы пробуем восстановить сессию через refresh-cookie
    useEffect(() => {
        authApi.refresh()
            .then(({ access }) => setAccessToken(access))
            .catch(() => {})
            .finally(() => setInitializing(false));
    }, []);

    const login = useCallback(async (username, password) => {
        const { access, user } = await authApi.login(username, password);
        setAccessToken(access);
        setUser(user);
    }, []);

    const logout = useCallback(async () => {
        await authApi.logout().catch(() => {});
        setAccessToken(null);
        setUser(null);
    }, []);

    return (
        <AuthContext.Provider value={{ accessToken, user, login, logout, initializing }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
