import { fetchWrapper } from '../helpers/fetch-wrapper.js';

const { ref } = Vue;

const template = `
<div class="link-preview">
    <a v-for="(unfurl, index) in unfurls" :key="index" :unfurl="unfurl" :href="unfurl.url">
        <p>{{ unfurl.values.join(" | ") }}</p>
    </a>
</div>
`;

export default  {
    name: 'LinkPreview',
    template,
    props: {
        message: Object,
    },
    setup (props) {
        const unfurls = ref([]);

        function parseUrls(message) {
            var pattern = /\w+:\/\/[^\s]+/gi;
            var matches = message.comment.match(pattern);
            return matches || [];
        };

        function doUnfurl(message) {
            var urls = parseUrls(message);
            urls.forEach((value, key) => {
                // remove punctuation from URLs ending a sentence
                var url = value.replace(/[!.?]+$/g, '');
                fetchWrapper.post(`${API_BASE_URL}/unfurl`, {url: url})
                .then(json => {
                    var unfurl = Object;
                    unfurl.url = json.url;
                    unfurl.values = [];
                    var keys = ['site_name', 'title', 'description'];
                    for (var k in keys) {
                        if (json[keys[k]] !== null) {
                            unfurl.values.push(json[keys[k]]);
                        };
                    };
                    if (unfurl.values.length > 0) {
                        unfurls.value.push(unfurl);
                    };
                })
                .catch(error => {});
            });
        };

        doUnfurl(props.message);

        return {
            unfurls,
        };
    },
};
