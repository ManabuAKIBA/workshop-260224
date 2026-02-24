/**
 * タイマー状態管理クラス
 * 
 * フロントエンド側のタイマー状態を管理し、UIの更新を行う
 */

class TimerManager {
    constructor() {
        this.status = null;
        this.pollInterval = null;
    }

    /**
     * タイマーを開始
     */
    async start() {
        try {
            this.status = await api.post('/api/timer/start');
            this.updateDisplay();
            this.startPolling();
        } catch (error) {
            console.error('Failed to start timer:', error);
        }
    }

    /**
     * タイマーを一時停止
     */
    async pause() {
        try {
            this.status = await api.post('/api/timer/pause');
            this.updateDisplay();
            this.stopPolling();
        } catch (error) {
            console.error('Failed to pause timer:', error);
        }
    }

    /**
     * タイマーを再開
     */
    async resume() {
        try {
            this.status = await api.post('/api/timer/resume');
            this.updateDisplay();
            this.startPolling();
        } catch (error) {
            console.error('Failed to resume timer:', error);
        }
    }

    /**
     * タイマーをリセット
     */
    async reset() {
        try {
            this.status = await api.post('/api/timer/reset');
            this.updateDisplay();
            this.stopPolling();
        } catch (error) {
            console.error('Failed to reset timer:', error);
        }
    }

    /**
     * タイマー状態を取得
     */
    async getStatus() {
        try {
            this.status = await api.get('/api/timer/status');
            this.updateDisplay();
        } catch (error) {
            console.error('Failed to get timer status:', error);
        }
    }

    /**
     * ポーリングを開始（1秒ごとに状態を取得）
     */
    startPolling() {
        if (this.pollInterval) {
            return;
        }
        this.pollInterval = setInterval(async () => {
            await this.getStatus();
        }, 1000);
    }

    /**
     * ポーリングを停止
     */
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    /**
     * 画面表示を更新
     */
    updateDisplay() {
        if (!this.status) {
            return;
        }

        const { state, display_time, is_paused, progress } = this.status;

        // 時間表示を更新
        const timerDisplay = document.getElementById('timerDisplay');
        if (timerDisplay) {
            timerDisplay.textContent = display_time;
        }

        // 状態ラベルを更新
        const stateLabel = document.getElementById('stateLabel');
        if (stateLabel) {
            if (state === 'work') {
                stateLabel.textContent = is_paused ? '一時停止中' : '作業中';
            } else if (state === 'break') {
                stateLabel.textContent = '休憩中';
            } else if (state === 'long_break') {
                stateLabel.textContent = '長休憩中';
            } else {
                stateLabel.textContent = '待機中';
            }
        }

        // ボタン表示を切り替え
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        
        if (state === 'stopped') {
            if (startBtn) startBtn.style.display = 'block';
            if (pauseBtn) pauseBtn.style.display = 'none';
        } else if (is_paused) {
            if (startBtn) {
                startBtn.style.display = 'block';
                startBtn.textContent = '再開';
            }
            if (pauseBtn) pauseBtn.style.display = 'none';
        } else {
            if (startBtn) {
                startBtn.style.display = 'none';
            }
            if (pauseBtn) pauseBtn.style.display = 'block';
        }

        // プログレスバーを更新（進捗率が存在する場合）
        if (typeof progress === 'number') {
            const progressCircle = document.querySelector('.progress-ring__circle');
            if (progressCircle) {
                const radius = progressCircle.r.baseVal.value;
                const circumference = 2 * Math.PI * radius;
                const offset = circumference * (1 - progress);
                progressCircle.style.strokeDasharray = circumference;
                progressCircle.style.strokeDashoffset = offset;
            }
        }
    }
}

const timerManager = new TimerManager();
