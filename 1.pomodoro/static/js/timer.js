/**
 * タイマー管理クラス
 * タイマーの状態管理とポーリング処理
 */
class TimerManager {
    constructor() {
        this.status = null;
        this.pollInterval = null;
    }

    /**
     * タイマー開始
     */
    async start() {
        try {
            this.status = await api.post('/timer/start');
            this.updateUI();
            this.startPolling();
        } catch (error) {
            console.error('Failed to start timer:', error);
        }
    }

    /**
     * タイマー一時停止
     */
    async pause() {
        try {
            this.status = await api.post('/timer/pause');
            this.updateUI();
            this.stopPolling();
        } catch (error) {
            console.error('Failed to pause timer:', error);
        }
    }

    /**
     * タイマー再開
     */
    async resume() {
        try {
            this.status = await api.post('/timer/resume');
            this.updateUI();
            this.startPolling();
        } catch (error) {
            console.error('Failed to resume timer:', error);
        }
    }

    /**
     * タイマーリセット
     */
    async reset() {
        try {
            this.status = await api.post('/timer/reset');
            this.updateUI();
            this.stopPolling();
        } catch (error) {
            console.error('Failed to reset timer:', error);
        }
    }

    /**
     * タイマー状態取得
     */
    async getStatus() {
        try {
            this.status = await api.get('/timer/status');
            this.updateUI();
        } catch (error) {
            console.error('Failed to get status:', error);
        }
    }

    /**
     * ポーリング開始（1秒ごと）
     */
    startPolling() {
        if (!this.pollInterval) {
            this.pollInterval = setInterval(() => {
                this.getStatus();
            }, 1000);  // 1秒ごと更新
        }
    }

    /**
     * ポーリング停止
     */
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    /**
     * UI更新
     */
    updateUI() {
        if (!this.status) {
            return;
        }

        const { display_time, progress, state, is_paused } = this.status;
        
        // タイマー表示更新
        const timerDisplay = document.getElementById('timerDisplay');
        if (timerDisplay) {
            timerDisplay.textContent = display_time;
        }

        // 状態ラベル更新
        const stateLabel = document.getElementById('stateLabel');
        if (stateLabel) {
            stateLabel.textContent = state === 'work' ? '作業中' : 
                                    state === 'break' ? '休憩中' : '停止中';
        }

        // ボタン表示切替
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        
        if (state === 'stopped') {
            if (startBtn) startBtn.style.display = 'inline-block';
            if (pauseBtn) pauseBtn.style.display = 'none';
        } else if (is_paused) {
            if (startBtn) {
                startBtn.textContent = '再開';
                startBtn.style.display = 'inline-block';
            }
            if (pauseBtn) pauseBtn.style.display = 'none';
        } else {
            if (startBtn) {
                startBtn.textContent = '開始';
                startBtn.style.display = 'none';
            }
            if (pauseBtn) pauseBtn.style.display = 'inline-block';
        }

        // 進捗バー更新（progressManagerが定義されている場合）
        if (typeof progressManager !== 'undefined' && progressManager) {
            progressManager.setProgress(progress);
        }
    }
}

// グローバルなタイマーマネージャーインスタンス
const timerManager = new TimerManager();
