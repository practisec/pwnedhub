const state = {
    apiUrl: "{{ config.API_BASE_URL }}",
    mail: Array(),
    messages: Array(),
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
};

const store = new Vuex.Store({
    state,
    mutations,
    actions,
    getters,
});

// global functions

function handleErrors(response) {
    if (response.ok) {
        return Promise.resolve(response);
    }
    return response.json().then(json => {
        var error = new Error(json.message || response.statusText)
        return Promise.reject(error.message)
    });
}
