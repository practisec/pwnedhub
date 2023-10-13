import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const AccessToken = {
    create(data) {
        return fetchWrapper.post(`${API_BASE_URL}/access-token`, data);
    },
    delete() {
        return fetchWrapper.delete(`${API_BASE_URL}/access-token`);
    },
};

const User = {
    all() {
        return fetchWrapper.get(`${API_BASE_URL}/users`);
    },
    get(uid) {
        return fetchWrapper.get(`${API_BASE_URL}/users/${uid}`);
    },
    create(data) {
        return fetchWrapper.post(`${API_BASE_URL}/users`, data);
    },
    update(uid, data) {
        return fetchWrapper.patch(`${API_BASE_URL}/users/${uid}`, data);
    },
};

const AdminUser = {
    update(uid, data) {
        return fetchWrapper.patch(`${API_BASE_URL}/admin/users/${uid}`, data);
    },
};

const Message = {
    all(rid, query) {
        return fetchWrapper.get(`${API_BASE_URL}/rooms/${rid}/messages${query}`);
    },
};

const LinkPreview = {
    create(data) {
        return fetchWrapper.post(`${API_BASE_URL}/unfurl`, data);
    },
};

const Note = {
    all() {
        return fetchWrapper.get(`${API_BASE_URL}/notes`);
    },
    replace(data) {
        return fetchWrapper.put(`${API_BASE_URL}/notes`, data);
    },
};

const Tool = {
    all() {
        return fetchWrapper.get(`${API_BASE_URL}/tools`);
    },
    create(data) {
        return fetchWrapper.post(`${API_BASE_URL}/tools`, data);
    },
    delete(tid) {
        return fetchWrapper.delete(`${API_BASE_URL}/tools/${tid}`);
    },
};

const Scan = {
    all() {
        return fetchWrapper.get(`${API_BASE_URL}/scans`);
    },
    get(sid) {
        return fetchWrapper.get(`${API_BASE_URL}/scans/${sid}/results`);
    },
    create(data) {
        return fetchWrapper.post(`${API_BASE_URL}/scans`, data);
    },
    delete(sid) {
        return fetchWrapper.delete(`${API_BASE_URL}/scans/${sid}`);
    },
};


export {
    AccessToken,
    User,
    AdminUser,
    Message,
    LinkPreview,
    Note,
    Tool,
    Scan,
};
