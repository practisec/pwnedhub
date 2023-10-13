import { useAuthStore } from '../stores/auth-store.js';
import { router } from '../router.js';

export const fetchWrapper = {
    get: request('GET'),
    post: request('POST'),
    put: request('PUT'),
    patch: request('PATCH'),
    delete: request('DELETE'),
};

function request(method) {
    return async (url, body) => {
        const options = {
            method: method,
            credentials: 'include',
            headers: {},
        };
        const authStore = useAuthStore();
        if (authStore.accessToken) {
            options.headers['Authorization'] = `Bearer ${authStore.accessToken}`;
        };
        if (authStore.csrfToken) {
            options.headers[CSRF_TOKEN_NAME] = authStore.csrfToken;
        };
        if (body) {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(body);
        };
        const response = await fetch(url, options);
        return handleErrors(response);
    };
};

async function handleErrors(response) {
    // handle empty responses
    if (response.status === 204) {
        return {};
    // handle good responses
    } else if (response.ok) {
        return await response.json();
    // route unauthenticated users to login
    } else if (response.status === 401) {
        const authStore = useAuthStore();
        authStore.unsetAuthInfo();
        router.push('login');
        throw new Error('Unauthenticated.');
    // treat everything else like an error
    } else {
        const json = await response.json();
        // handle Passwordless
        if (json.error === 'code_required') {
            const authStore = useAuthStore();
            authStore.setCodeToken(json.code_token);
            router.push({ name: 'passwordless', params: { nextUrl: router.currentRoute.value.params.nextUrl } });
            throw new Error('Code required for Passwordless Authentication.');
        // raise an error to trigger the catch block
        } else {
            throw new Error(json.message || response.statusText);
        };
    };
};
