"use client";

export const AUTH_TOKEN_KEY = 'aisec_token';

export function setAccessToken(token: string) {
    if (typeof window !== 'undefined') {
        localStorage.setItem(AUTH_TOKEN_KEY, token);
        // Also set a cookie for middleware access
        document.cookie = `${AUTH_TOKEN_KEY}=${token}; path=/; max-age=86400; SameSite=Lax`;
    }
}

export function getAccessToken(): string | null {
    if (typeof window !== 'undefined') {
        return localStorage.getItem(AUTH_TOKEN_KEY);
    }
    return null;
}

export function removeAccessToken() {
    if (typeof window !== 'undefined') {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        document.cookie = `${AUTH_TOKEN_KEY}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
    }
}

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
    const token = getAccessToken();
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    };

    const response = await fetch(url, { ...options, headers });
    
    if (response.status === 401) {
        removeAccessToken();
        if (typeof window !== 'undefined') {
            window.location.href = '/login';
        }
    }
    
    return response;
}
