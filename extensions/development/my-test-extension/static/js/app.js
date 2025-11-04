// uDOS Extension Template JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const statusBtn = document.getElementById('status-btn');
    const infoBtn = document.getElementById('info-btn');
    const output = document.getElementById('output');

    // API helper function
    async function callAPI(endpoint) {
        try {
            const response = await fetch(`/api/${endpoint}`);
            const data = await response.json();
            return data;
        } catch (error) {
            return { error: `Failed to fetch ${endpoint}: ${error.message}` };
        }
    }

    // Display result in output area
    function displayResult(data) {
        output.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    }

    // Event listeners
    statusBtn.addEventListener('click', async function() {
        output.innerHTML = '<p>🔄 Checking status...</p>';
        const result = await callAPI('status');
        displayResult(result);
    });

    infoBtn.addEventListener('click', async function() {
        output.innerHTML = '<p>🔄 Getting extension info...</p>';
        const result = await callAPI('info');
        displayResult(result);
    });

    // Welcome message
    output.innerHTML = '<p>🌟 Welcome to your new uDOS extension!</p><p>Click the buttons above to test the API endpoints.</p>';
});
