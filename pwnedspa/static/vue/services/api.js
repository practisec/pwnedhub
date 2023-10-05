import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const AccessToken = {
    create(data) {
        return fetchWrapper.post(`${API_BASE_URL}/access-token`, data)
    },
    delete() {
        return fetchWrapper.delete(`${API_BASE_URL}/access-token`);
    }
}

const User = {
    get(id) {
        return fetchWrapper.get(`${API_BASE_URL}/users/${id}`)
    }
}

export {
    AccessToken,
    User,
}

/*
import axios from 'axios';

const User = {
    all() {
        return axios.get('/api/v1/users/');
    },
    get(id) {
        return axios.get(`/api/v1/users/${id}`);
    },
    create(id, data) {
        return axios.post('/api/v1/users', data);
    }
}

export {
    User,
}
*/
