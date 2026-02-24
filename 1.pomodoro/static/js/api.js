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
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return response.json();
        } catch (error) {
            console.error('API POST request failed:', error);
            throw error;
        }
    }

    /**
     * GETリクエストを送信
     * 
     * @param {string} endpoint - APIエンドポイント
     * @returns {Promise<Object>} レスポンスJSON
     */
    async get(endpoint) {
        try {
            const response = await fetch(endpoint);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return response.json();
        } catch (error) {
            console.error('API GET request failed:', error);
            throw error;
        }
    }
}

const api = new APIClient();
