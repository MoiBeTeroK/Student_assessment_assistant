let _token = null;
let _refreshFn = null;

export const tokenStore = {
    get: () => _token,
    set: (token) => { _token = token; },
    setRefreshFn: (fn) => { _refreshFn = fn; },
    refresh: () => _refreshFn?.(),
};
