import { LinkPreview } from '../services/api.js';

const { ref } = Vue;

const template = `
<div class="link-preview">
    <a v-for="(preview, index) in previews" :key="index" :preview="preview" :href="preview.url">
        <p>{{ preview.values.join(" | ") }}</p>
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
        const previews = ref([]);

        function parseUrls(message) {
            var pattern = /\w+:\/\/[^\s]+/gi;
            var matches = message.comment.match(pattern);
            return matches || [];
        };

        async function doPreview(message) {
            const urls = parseUrls(message);
            for (let url of urls) {
                // remove punctuation from URLs ending a sentence
                const sanitizedUrl = url.replace(/[!.?]+$/g, '');
                try {
                    const json = await LinkPreview.create({url: sanitizedUrl});
                    const preview = {
                        url: json.url,
                        values: []
                    };
                    const keys = ['site_name', 'title', 'description'];
                    for (let key of keys) {
                        if (json[key] !== null) {
                            preview.values.push(json[key]);
                        };
                    };
                    if (preview.values.length > 0) {
                        previews.value.push(preview);
                    };
                } catch (error) {};
            };
        };

        doPreview(props.message);

        return {
            previews,
        };
    },
};
