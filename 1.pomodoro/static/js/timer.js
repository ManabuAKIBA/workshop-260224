/**
 * TimerManager - タイマーの状態管理とUI更新
 * プログレスバーと連携してリアルタイム更新を行う
 */
class TimerManager {
    constructor(apiClient, progressManager) {
        this.api = apiClient;
        this.progress = progressManager;
        
        // UI要素の取得
        this.timerDisplay = document.getElementById('timerDisplay');
        this.stateLabel = document.getElementById('stateLabel');
        this.startBtn = document.getElementById('startBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        
        // ポーリング用
        this.pollingInterval = null;
        this.isRunning = false;
    }

    /**
     * タイマーを開始
     */
    async start() {
        try {
            const result = await this.api.post('/api/timer/start');
            
            if (result.success || result.state) {
                this.isRunning = true;
                this.updateButtonStates(true);
                this.startPolling();
                this.updateDisplay(result);
            }
        } catch (error) {
            console.error('Failed to start timer:', error);
        }
    }

    /**
     * タイマーをリセット
     */
    async reset() {
        try {
            // ポーリングを停止
            this.stopPolling();
            
            // APIでリセット（実装されている場合）
            // await this.api.post('/api/timer/reset');
            
            // UI をリセット
            this.isRunning = false;
            this.updateButtonStates(false);
            this.timerDisplay.textContent = '25:00';
            this.stateLabel.textContent = '作業中';
            this.progress.reset();
        } catch (error) {
            console.error('Failed to reset timer:', error);
        }
    }

    /**
     * ポーリングを開始（1秒ごとにステータスを取得）
     */
    startPolling() {
        // 既存のポーリングをクリア
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        // 1秒ごとにステータスを取得
        this.pollingInterval = setInterval(async () => {
            await this.updateStatus();
        }, 1000);
    }

    /**
     * ポーリングを停止
     */
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    /**
     * タイマーステータスを更新
     */
    async updateStatus() {
        try {
            const status = await this.api.get('/api/timer/status');
            this.updateDisplay(status);
            
            // タイマーが完了した場合、ポーリングを停止
            if (status.is_completed) {
                this.stopPolling();
                this.isRunning = false;
                this.updateButtonStates(false);
            }
        } catch (error) {
            console.error('Failed to update status:', error);
        }
    }

    /**
     * 表示を更新
     * @param {Object} data - タイマーステータスデータ
     */
    updateDisplay(data) {
        // 残り時間を更新
        if (data.display_time) {
            this.timerDisplay.textContent = data.display_time;
        }
        
        // 状態ラベルを更新
        if (data.state) {
            const stateLabels = {
                'work': '作業中',
                'break': '休憩中',
                'long_break': '長休憩中',
                'stopped': '停止'
            };
            this.stateLabel.textContent = stateLabels[data.state] || '作業中';
        }
        
        // プログレスバーを更新
        if (data.progress !== undefined) {
            this.progress.setProgress(data.progress);
        }
    }

    /**
     * ボタンの表示状態を更新
     * @param {boolean} running - タイマーが実行中かどうか
     */
    updateButtonStates(running) {
        if (running) {
            this.startBtn.style.display = 'none';
            this.pauseBtn.style.display = 'inline-block';
        } else {
            this.startBtn.style.display = 'inline-block';
            this.pauseBtn.style.display = 'none';
        }
    }
}
