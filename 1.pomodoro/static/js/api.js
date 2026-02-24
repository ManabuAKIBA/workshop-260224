/**
 * APIクライアント
 * fetch APIのラッパー
 */
class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    /**
     * GETリクエスト
     * @param {string} endpoint - エンドポイントパス
     * @returns {Promise<any>} - レスポンスデータ
     */
    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API GET error:', error);
            throw error;
        }
    }

    /**
     * POSTリクエスト
     * @param {string} endpoint - エンドポイントパス
     * @param {object} data - 送信データ（オプション）
     * @returns {Promise<any>} - レスポンスデータ
     */
    async post(endpoint, data = null) {
        try {
            const options = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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
            console.error('API POST error:', error);
            throw error;
        }
    }
}

// グローバルなAPIクライアントインスタンス
const api = new APIClient();
