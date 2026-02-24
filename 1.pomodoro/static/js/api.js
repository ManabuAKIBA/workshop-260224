/**
 * API クライアント
 * 
 * バックエンド API との通信を担当するクラス
 */

class APIClient {
    /**
     * API クライアントを初期化
     * 
     * @param {string} baseURL - API のベース URL（デフォルト: '/api'）
     */
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    /**
     * GET リクエストを送信
     * 
     * @param {string} endpoint - エンドポイント（例: '/timer/status'）
     * @returns {Promise<Object>} レスポンスデータ
     */
    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('GET request failed:', error);
            throw error;
        }
    }

    /**
     * POST リクエストを送信
     * 
     * @param {string} endpoint - エンドポイント（例: '/timer/start'）
     * @param {Object} data - 送信するデータ（オプション）
     * @returns {Promise<Object>} レスポンスデータ
     */
    async post(endpoint, data = null) {
        try {
            const options = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.baseURL}${endpoint}`, options);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('POST request failed:', error);
            throw error;
        }
    }
}
