const template = `
<div class="scans-modal">
    <pre v-html="results"></pre>
</div>
`;

export default {
    name: 'ScansModal',
    template,
    props: {
        results: String,
    },
};
