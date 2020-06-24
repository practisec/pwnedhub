const state = {
    apiUrl: API_BASE_URL,
    mail: [],
    messages: [],
    userInfo: null,
    authHeader: {},
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
    UPDATE_MESSAGES(state, payload) {
        state.messages = payload;
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
};

const actions = {
    updateMail(context, mail) {
        context.commit("UPDATE_MAIL", mail);
    },
    updateLetter(context, letter) {
        context.commit("UPDATE_LETTER", letter);
    },
    updateMessages(context, messages) {
        context.commit("UPDATE_MESSAGES", messages);
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
    getMessages(state) {
        return state.messages;
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
