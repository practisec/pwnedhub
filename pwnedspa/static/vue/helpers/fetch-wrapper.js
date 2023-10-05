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
    return (url, body) => {
        var options = {};
        options.method = method;
        options.credentials = 'include';
        options.headers = {};
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
        return fetch(url, options).then(handleErrors);
    };
};

function handleErrors(response) {
    // handle empty responses
    if (response.status === 204) {
        return Promise.resolve({});
    // handle good responses
    } else if (response.ok) {
        return Promise.resolve(response.json());
    // route unauthenticated users to login
    } else if (response.status === 401) {
        const authStore = useAuthStore();
        authStore.unsetAuthInfo();
        router.push('login');
        breakPromiseChain();
    // treat everything else like an error
    } else {
        return response.json().then(json => {
            // handle Passwordless
            if (json.error === 'code_required') {
                const authStore = useAuthStore();
                authStore.setCodeToken(json.code_token);
                router.push({ name: 'passwordless', params: { nextUrl: router.currentRoute.value.params.nextUrl } });
                breakPromiseChain();
            // reject back to the catch callback
            } else {
                var error = new Error(json.message || response.statusText);
                return Promise.reject(error.message);
            };
        });
    };
};

function breakPromiseChain() {
    // hack to break the promise chain
    // see createToast in app-store.js
    var error = new Error();
    error.name = 'BreakPromiseChain';
    throw error;
};
