export const storage = {
    get: (key) => {
        try {
            const val = localStorage.getItem(key);
            return val ? JSON.parse(val) : null;
        } catch {
            return null;
        }
    },
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch {}
    },
};