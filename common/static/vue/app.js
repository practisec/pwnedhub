// override and wrap fetch
var _fetch = window.fetch;
window.fetch = function(url, options) {
    var options = options || {};
    options.headers = {
        ...store.getters.getAuthHeader,
        ...store.getters.getCsrfHeader,
        ...options.headers || {},
    }
    return _fetch(url, options);
}

function handleErrors(response) {
    if (response.ok) {
        return Promise.resolve(response);
    }
    if (response.status === 401) {
        store.dispatch("unsetAuthInfo");
        router.push("login");
    }
    return response.json().then(json => {
        var error = new Error(json.message || response.statusText)
        return Promise.reject(error.message)
    });
}

const socket = io(API_BASE_URL, {
    autoConnect: false,
    transports: ['websocket'],
    query: {},
});

Vue.use(VueSocketIOExt, socket);

const app = new Vue({
    el: "#app",
    router,
});
