/**
 * APIClient - バックエンドAPIとの通信を担当
 */
class APIClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    /**
     * GETリクエスト
     * @param {string} endpoint - APIエンドポイント
     * @returns {Promise<Object>} レスポンスデータ
     */
    async get(endpoint) {
        try {
            const response = await fetch(this.baseUrl + endpoint, {
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
     * POSTリクエスト
     * @param {string} endpoint - APIエンドポイント
     * @param {Object} data - 送信データ（オプション）
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
            
            const response = await fetch(this.baseUrl + endpoint, options);
            
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
