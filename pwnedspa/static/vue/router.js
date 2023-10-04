import Signup from './views/signup.js';
import Activate from './views/activate.js';
import Login from './views/login.js';
import PasswordlessAuth from './views/passwordless.js';
import Account from './views/account.js';
import Profile from './views/profile.js';
import Notes from './views/notes.js';
import Scans from './views/scans.js';
import Messaging from './views/messages.js';
import Tools from './views/tools.js'
import Users from './views/users.js'
import { useAuthStore } from './stores/auth-store.js';

const { createRouter, createWebHashHistory } = VueRouter;
const routes = [
    {
        path: '/signup',
        name: 'signup',
        component: Signup,
    },
    {
        path: '/signup/activate/:activateToken',
        name: 'activate',
        component: Activate,
        props: true,
    },
    {
        path: '/login',
        name: 'login',
        component: Login,
    },
    {
        path: '/login/passwordless',
        name: 'passwordless',
        component: PasswordlessAuth,
    },
    {
        path: '/account',
        name: 'account',
        component: Account,
        meta: {
            authRequired: true,
        },
    },
    {
        path: '/profile/:userId',
        name: 'profile',
        component: Profile,
        props: true,
        meta: {
            authRequired: true,
        },
    },
    {
        path: '/notes',
        name: 'notes',
        component: Notes,
        meta: {
            authRequired: true,
        },
    },
    {
        path: '/scans',
        name: 'scans',
        component: Scans,
        meta: {
            authRequired: true,
        },
    },
    {
        path: '/messaging',
        name: 'messaging',
        component: Messaging,
        meta: {
            authRequired: true,
        },
    },
    {
        path: '/admin/tools',
        name: 'tools',
        component: Tools,
        meta: {
            authRequired: true,
        },
    },
    {
        path: '/admin/users',
        name: 'users',
        component: Users,
        meta: {
            authRequired: true,
        },
    },
    {
        path: '/:catchAll(.*)',
        redirect: '/login',
    },
];

export const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    if (to.matched.some(record => record.meta.authRequired)) {
        if (!authStore.isLoggedIn) {
            next({
                name: 'login',
                params: { nextUrl: to.fullPath }
            });
        } else {
            next();
        };
    } else {
        // the login/passwordless views use similar logic to handle routing of the nextUrl parameter
        // all must be updated if there is a change
        if (authStore.isLoggedIn) {
            if (authStore.isAdmin) {
                next({ name: 'users' });
            };
            next({ name: 'notes' });
        } else {
            next();
        };
    };
});
