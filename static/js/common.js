// Shared helpers for every page.

function getToken() {
    return localStorage.getItem("token");
}

// JWTs use base64url encoding, which atob() can't read directly.
function decodeTokenPayload(token) {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(base64.padEnd(base64.length + (4 - base64.length % 4) % 4, '=')));
}

function isTokenExpired(token) {
    if (!token) return true;
    try {
        return Date.now() > decodeTokenPayload(token).exp * 1000;
    } catch (error) {
        return true;
    }
}

function redirectToLogin(message) {
    localStorage.removeItem("token");
    if (message) alert(message);
    window.location.href = "/login-page";
}

// Redirects to the login page (and returns null) if there is no valid token.
function requireToken() {
    const token = getToken();
    if (isTokenExpired(token)) {
        redirectToLogin(token ? "Your session has expired. Please log in again." : null);
        return null;
    }
    return token;
}

// fetch() with the Authorization header added. Sends the user to the login page on a 401.
async function authFetch(url, options = {}) {
    const token = requireToken();
    if (!token) return null;
    const headers = { ...(options.headers || {}), "Authorization": `Bearer ${token}` };
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
        redirectToLogin("Your session has expired. Please log in again.");
        return null;
    }
    return response;
}

async function errorMessage(response) {
    try {
        const body = await response.json();
        if (Array.isArray(body.detail)) return body.detail.map(d => d.msg).join("; ");
        return body.detail || response.statusText;
    } catch (error) {
        return response.statusText;
    }
}

// Escape user-entered text before inserting it into HTML.
function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}
