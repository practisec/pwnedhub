import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const AccessToken = {
    create(data) {
        return fetchWrapper.post(`${API_BASE_URL}/access-token`, data)
    },
}

export {
    AccessToken,
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
