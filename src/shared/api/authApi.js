import { tokenStore } from './tokenStore';

const request = async (url, options = {}) => {
    const res = await fetch(url, { credentials: 'include', ...options });
    if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Ошибка запроса');
    }
    return res.json();
};

export const authApi = {
    login: (username, password) =>
        request('/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        }),

    refresh: () =>
        request('/api/auth/refresh/', { method: 'POST' }),

    logout: () =>
        fetch('/api/auth/logout/', { method: 'POST', credentials: 'include' }),
};

// Fetch-обёртка с автоматическим обновлением токена при 401
export const apiFetch = async (url, options = {}) => {
    const doRequest = (token) =>
        fetch(url, {
            credentials: 'include',
            ...options,
            headers: {
                ...options.headers,
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
        });

    let res = await doRequest(tokenStore.get());

    if (res.status === 401) {
        const newToken = await tokenStore.refresh();
        if (newToken) {
            res = await doRequest(newToken);
        }
    }

    return res;
};
