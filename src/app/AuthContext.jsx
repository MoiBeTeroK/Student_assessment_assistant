import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { authApi } from '../shared/api/authApi';
import { tokenStore } from '../shared/api/tokenStore';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [accessToken, setAccessToken] = useState(null);
    const [user, setUser] = useState(null);
    const [initializing, setInitializing] = useState(true);

    // Синхронизируем токен в модульное хранилище при каждом изменении
    useEffect(() => {
        tokenStore.set(accessToken);
    }, [accessToken]);

    // Регистрируем функцию обновления токена для apiFetch
    useEffect(() => {
        tokenStore.setRefreshFn(async () => {
            try {
                const { access } = await authApi.refresh();
                setAccessToken(access);
                return access;
            } catch {
                setAccessToken(null);
                setUser(null);
                return null;
            }
        });
    }, []);

    // При загрузке страницы восстанавливаем сессию через refresh-cookie
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
