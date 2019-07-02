// global constants mixin
// requires vue.js library
// place between vue and custom component code

// can also be done using a JS object, but would
// require importing via the "data" attribute

Vue.mixin({
    data: function() {
        return {
            get URL_API_BASE() { return "{{ config.API_BASE_URL }}" },
            get URL_IMG_INBOX() { return "{{ url_for('static', filename='images/inbox.png') }}"; },
            get URL_IMG_VIEW() { return "{{ url_for('static', filename='images/view.png') }}"; },
            get URL_IMG_REPLY() { return "{{ url_for('static', filename='images/reply.png') }}"; },
            get URL_IMG_SEND() { return "{{ url_for('static', filename='images/send.png') }}"; },
            get URL_IMG_DELETE() { return "{{ url_for('static', filename='images/delete.png') }}"; },
        }
    },
});

// global functions

function handleErrors(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}
