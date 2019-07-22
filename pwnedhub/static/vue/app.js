function handleErrors(response) {
    if (response.ok) {
        return Promise.resolve(response);
    }
    if (response.status === 401) {
        store.dispatch("unsetUserInfo");
        router.push("login");
    }
    return response.json().then(json => {
        var error = new Error(json.message || response.statusText)
        return Promise.reject(error.message)
    });
}

const app = new Vue({
    el: "#app",
    router,
});
