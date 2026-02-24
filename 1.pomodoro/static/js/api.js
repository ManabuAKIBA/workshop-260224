// static/js/api.js
class APIClient {
    async post(endpoint, data = {}) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }

    async get(endpoint) {
        const response = await fetch(endpoint);
        return response.json();
    }
}

const api = new APIClient();
