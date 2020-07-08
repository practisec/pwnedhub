const state = {
    apiUrl: API_BASE_URL,
    mail: [],
    toasts: [],
    userInfo: null,
    authHeader: {},
    modalVisible: false,
    modalComponent: null,
    modalParams: {},
}

const mutations = {
    UPDATE_MAIL(state, payload) {
        state.mail = payload;
    },
    UPDATE_LETTER(state, payload) {
        var index = state.mail.findIndex(function(letter) {
            return letter.id === payload.id;
        })
        state.mail[index] = payload;
    },
    CREATE_TOAST(state, toast) {
        state.toasts.push(toast)
    },
    REMOVE_TOAST(state, id) {
        state.toasts = state.toasts.filter(t => t.id !== id)
    },
    SET_USER_INFO(state, value) {
        state.userInfo = value;
        localStorage.setItem("user", JSON.stringify(value));
    },
    UNSET_USER_INFO(state) {
        state.userInfo = null
        localStorage.removeItem("user");
    },
    SET_AUTH_HEADER(state, token) {
        state.authHeader = {"Authorization": "Bearer "+token};
        localStorage.setItem("token", JSON.stringify(token));
    },
    UNSET_AUTH_HEADER(state) {
        state.authHeader = {};
        localStorage.removeItem("token");
    },
    SHOW_MODAL(state, payload) {
        state.modalVisible = true;
        state.modalComponent = payload.componentName;
        state.modalParams = payload.params;
    },
    HIDE_MODAL(state) {
        state.modalVisible = false;
        state.modalComponent = null;
        state.modalParams = {};
    },
};

let maxToastId = 0;

const actions = {
    updateMail(context, mail) {
        context.commit("UPDATE_MAIL", mail);
    },
    updateLetter(context, letter) {
        context.commit("UPDATE_LETTER", letter);
    },
    createToast(context, text) {
        // handle non-string input such as errors
        // errors from processing successful responses can end up here
        if (typeof(text) != "string") {
            console.error(text);
            return
        }
        const id = ++maxToastId;
        context.commit("CREATE_TOAST", {id: id, text: text});
        setTimeout(() => {
            context.commit("REMOVE_TOAST", id);
        }, 5000)
    },
    setAuthInfo(context, json) {
        context.commit("SET_USER_INFO", json.user);
        if (json.token) {
            context.commit("SET_AUTH_HEADER", json.token);
        }
    },
    unsetAuthInfo(context) {
        context.commit("UNSET_USER_INFO");
        context.commit("UNSET_AUTH_HEADER");
    },
    initAuthInfo(context) {
        // initialize user info
        var user = JSON.parse(localStorage.getItem("user"));
        if (user != null) {
            context.commit("SET_USER_INFO", user);
            // initialize access token (if necessary)
            var token = JSON.parse(localStorage.getItem("token"));
            if (token != null) {
                context.commit("SET_AUTH_HEADER", token);
            }
        }
    },
    showModal(context, payload) {
        context.commit("SHOW_MODAL", payload);
    },
    hideModal(context) {
        context.commit("HIDE_MODAL");
    },
};

const getters = {
    getApiUrl(state) {
        return state.apiUrl;
    },
    getMail(state) {
        return state.mail;
    },
    getLetter(state) {
        return function(id) {
            return state.mail.find(function(letter) {
                return letter.id === id;
            });
        };
    },
    getToasts(stats) {
        return state.toasts;
    },
    getUserInfo(state) {
        return state.userInfo;
    },
    getAuthHeader(state) {
        return state.authHeader;
    },
    isLoggedIn(state, getters) {
        if (getters.getUserInfo === null) {
            return false;
        }
        return true;
    },
    isAdmin: function(state, getters) {
        if (getters.isLoggedIn) {
            user = getters.getUserInfo;
            return (user.role === "admin") ? true : false;
        }
        return false;
    },
    getUserRole: function(state, getters) {
        if (getters.isLoggedIn) {
            return store.getters.getUserInfo.role;
        }
        return "guest";
    },
    modalVisible(state) {
        return state.modalVisible;
    },
    modalComponent(state) {
        return state.modalComponent;
    },
    modalParams(state) {
        return state.modalParams;
    },
};

const store = new Vuex.Store({
    state,
    mutations,
    actions,
    getters,
});

// initialize the store prior to instantiating the app to ensure
// the router.beforeEach check gets the proper isLoggedIn value
store.dispatch("initAuthInfo");
