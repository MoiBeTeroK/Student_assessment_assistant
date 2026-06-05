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
