// global constants mixin
// requires vue.js library
// place between vue and custom component code

// can also be done using a JS object, but would
// require importing via the "data" attribute

Vue.mixin({
    data: function() {
        return {
            get URL_API_USER_READ() { return "{{ url_for('api.user_read', uid='{0}') | urldecode }}" },
            get URL_API_USERS_READ() { return "{{ url_for('api.users_read') }}" },
            get URL_API_MAILBOX_READ() { return "{{ url_for('api.mailbox_read') }}" },
            get URL_API_MAIL_CREATE() { return "{{ url_for('api.mail_create') }}" },
            get URL_API_MAIL_READ() { return "{{ url_for('api.mail_read', mid='{0}') | urldecode }}" },
            get URL_API_MAIL_DELETE() { return "{{ url_for('api.mail_delete', mid='{0}') | urldecode }}" },
            get URL_API_MESSAGES_READ() { return "{{ url_for('api.messages_read') }}" },
            get URL_API_MESSAGE_CREATE() { return "{{ url_for('api.message_create') }}" },
            get URL_API_MESSAGE_DELETE() { return "{{ url_for('api.message_delete', mid='{0}') | urldecode }}"; },
            get URL_API_UNFURL() { return "{{ url_for('api.unfurl') }}" },
            get URL_IMG_TRASH() { return "{{ url_for('static', filename='images/trash.png') }}"; },
        }
    },
});
