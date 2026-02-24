/**
 * タイマー管理
 * 
 * ポモドーロタイマーのフロントエンド管理を担当するクラス
 */

class TimerManager {
    /**
     * タイマーマネージャーを初期化
     * 
     * @param {APIClient} apiClient - API クライアントインスタンス
     */
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.pollingInterval = null;
        this.isPolling = false;
        this.lastCompletedState = null; // 最後に完了したセッションの状態を記録
        
        // デフォルトのセッション時間（分）
        this.sessionDurations = {
            'work': 25,
            'break': 5,
            'long_break': 15
        };
    }

    /**
     * タイマーを開始
     * 
     * @returns {Promise<Object>} 開始結果
     */
    async start() {
        try {
            const result = await this.apiClient.post('/timer/start');
            console.log('Timer started:', result);
            
            // ポーリング開始
            this.startPolling();
            
            return result;
        } catch (error) {
            console.error('Failed to start timer:', error);
            throw error;
        }
    }

    /**
     * タイマーの状態を取得
     * 
     * @returns {Promise<Object>} タイマー状態
     */
    async getStatus() {
        try {
            return await this.apiClient.get('/timer/status');
        } catch (error) {
            console.error('Failed to get timer status:', error);
            throw error;
        }
    }

    /**
     * セッション完了を記録
     * 
     * @param {string} sessionType - セッション種類（work/break/long_break）
     * @param {number} durationMinutes - セッション時間（分）
     * @returns {Promise<Object>} 完了結果
     */
    async completeSession(sessionType, durationMinutes) {
        try {
            const result = await this.apiClient.post('/session/complete', {
                session_type: sessionType,
                duration_minutes: durationMinutes
            });
            console.log('Session completed:', result);
            return result;
        } catch (error) {
            console.error('Failed to complete session:', error);
            throw error;
        }
    }

    /**
     * ポーリングを開始（1秒ごとにタイマー状態を取得）
     */
    startPolling() {
        if (this.isPolling) {
            return;
        }

        this.isPolling = true;
        this.pollingInterval = setInterval(async () => {
            try {
                const status = await this.getStatus();
                
                // カスタムイベントを発火してステータスを通知
                const event = new CustomEvent('timer-update', { 
                    detail: status 
                });
                document.dispatchEvent(event);

                // タイマー完了時の処理
                // 有効なセッションタイプのみ記録
                const validSessionTypes = ['work', 'break', 'long_break'];
                if (status.is_completed && validSessionTypes.includes(status.state)) {
                    // 同じセッションを二重に記録しないようにチェック
                    if (this.lastCompletedState !== status.state) {
                        console.log('Timer completed! Recording session...');
                        
                        // セッションタイプに応じた時間を取得
                        const duration = this.sessionDurations[status.state] || 25;
                        
                        // セッション完了を記録
                        await this.completeSession(status.state, duration);
                        
                        // 完了した状態を記録
                        this.lastCompletedState = status.state;
                        
                        // 統計更新イベントを発火
                        const statsEvent = new CustomEvent('stats-update');
                        document.dispatchEvent(statsEvent);
                    }
                }
                
                // タイマーがリセットされた場合は状態をクリア
                if (!status.is_completed) {
                    this.lastCompletedState = null;
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, 1000);
    }

    /**
     * ポーリングを停止
     */
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            this.isPolling = false;
        }
    }
}
