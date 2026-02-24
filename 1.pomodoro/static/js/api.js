/**
 * API通信クライアント
 * 
 * フロントエンドからバックエンドAPIへの通信を抽象化
 */

class APIClient {
    /**
     * POSTリクエストを送信
     * 
     * @param {string} endpoint - APIエンドポイント
     * @param {Object} data - 送信するデータ
     * @returns {Promise<Object>} レスポンスJSON
     */
    async post(endpoint, data = {}) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }

    /**
     * GETリクエストを送信
     * 
     * @param {string} endpoint - APIエンドポイント
     * @returns {Promise<Object>} レスポンスJSON
     */
    async get(endpoint) {
        const response = await fetch(endpoint);
        return response.json();
    }
}

const api = new APIClient();
