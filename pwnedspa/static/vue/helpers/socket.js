import { io } from '../libs/socket.io.js'; // esm build

export const socket = io(API_BASE_URL, {
    autoConnect: false,
    transports: ['websocket'],
    query: {},
});
