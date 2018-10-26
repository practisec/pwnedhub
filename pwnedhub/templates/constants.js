// global constants mixin
// requires vue.js library
// place between vue and custom component code

Vue.mixin({
    data: function() {
        return {
            get URL_API_USERS_GET() { return "{{ url_for('api.users-get') }}" },
            get URL_API_MESSAGES_GET() { return "{{ url_for('api.messages-get') }}" },
            get URL_API_MESSAGES_POST() { return "{{ url_for('api.messages-post') }}" },
            get URL_API_MESSAGES_DELETE() { return "{{ url_for('api.messages-delete', mid='{0}') | urldecode }}"; },
            get URL_API_UNFURL() { return "{{ url_for('api.unfurl') }}" },
            get URL_IMG_TRASH() { return "{{ url_for('static', filename='images/trash.png') }}"; },
        }
    },
})
