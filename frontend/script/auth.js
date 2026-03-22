// auth.js - simple auth helpers for UI: register, login, logout, token storage
const authApi = '/api/v1/users';

// Generic fetch wrapper that includes credentials and handles 401 (token expired)
async function apiFetch(path, options = {}) {
    options.credentials = options.credentials || 'include';
    const res = await fetch(path, options);
    if (res.status === 401) {
        // try to clear cookie on server side
        try {
            await fetch(`${authApi}/logout`, {method: 'POST', credentials: 'include'});
        } catch (_) {}
        // clear local storage and redirect to login
        clearToken();
        localStorage.removeItem('auth_user');
        window.location.href = '/login';
        return res;
    }
    return res;
}

// expose as global for non-module scripts
window.apiFetch = apiFetch;

function setToken(token) {
    localStorage.setItem('access_token', token);
    // update nav UI
    _updateAuthUI();
}

function clearToken() {
    localStorage.removeItem('access_token');
    _updateAuthUI();
}

function getToken() {
    return localStorage.getItem('access_token');
}

async function registerUI(email, password) {
    // keep previous register behavior (returns created user)
    const res = await apiFetch(`${authApi}/register?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`, {
        method: 'POST'
    });
    return res;
}

async function loginUI(email, password) {
    // We send form as x-www-form-urlencoded; server sets HttpOnly cookie
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);
    const res = await apiFetch(`${authApi}/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: form.toString(),
    });
    if (!res.ok) return res;
    const data = await res.json();
    // store only non-sensitive user info locally (not the token) for UI
    if (data && data.user) localStorage.setItem('auth_user', JSON.stringify(data.user));
    _updateAuthUI();
    return res;
}

function _updateAuthUI() {
    const user = localStorage.getItem('auth_user');
    const navLogin = document.getElementById('navLogin');
    const navRegister = document.getElementById('navRegister');
    const navLogout = document.getElementById('navLogout');
    if (!navLogin || !navRegister || !navLogout) return;
    if (user) {
        navLogin.style.display = 'none';
        navRegister.style.display = 'none';
        navLogout.style.display = 'inline';
    } else {
        navLogin.style.display = 'inline';
        navRegister.style.display = 'inline';
        navLogout.style.display = 'none';
    }
}

// attach logout handler if present
document.addEventListener('DOMContentLoaded', () => {
    const navLogout = document.getElementById('navLogout');
    if (navLogout) {
        navLogout.addEventListener('click', async () => {
            // call backend to clear cookie
            try {
                                await apiFetch(`${authApi}/logout`, {method: 'POST'});
            } catch (_) {
            }
            clearToken();
            localStorage.removeItem('auth_user');
            // redirect to home
            window.location.href = '/';
        });
    }
    _updateAuthUI();
});

function getStoredUser() {
    const u = localStorage.getItem('auth_user');
    return u ? JSON.parse(u) : null;
}

// expose helpers
window.authUI = {registerUI, loginUI, logout: clearToken, getStoredUser};

