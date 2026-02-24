// static/js/timer.js
class TimerManager {
    constructor() {
        this.status = null;
        this.pollInterval = null;
    }

    async start() {
        this.status = await api.post('/api/timer/start');
        this.updateUI();
        this.startPolling();
    }

    async pause() {
        this.status = await api.post('/api/timer/pause');
        this.stopPolling();
        this.updateUI();
    }

    async resume() {
        this.status = await api.post('/api/timer/resume');
        this.startPolling();
        this.updateUI();
    }

    async reset() {
        this.status = await api.post('/api/timer/reset');
        this.stopPolling();
        this.updateUI();
    }

    async getStatus() {
        this.status = await api.get('/api/timer/status');
        this.updateUI();
    }

    startPolling() {
        if (!this.pollInterval) {
            this.pollInterval = setInterval(() => {
                this.getStatus();
            }, 1000);  // 1秒ごと更新
        }
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    updateUI() {
        if (!this.status) {
            console.error('Timer status is not available');
            return;
        }
        
        const { display_time, progress, state, is_paused } = this.status;
        
        document.getElementById('timerDisplay').textContent = display_time;
        document.getElementById('stateLabel').textContent = 
            state === 'work' ? '作業中' : '休憩中';
        
        // ボタン表示切替
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        
        if (state === 'stopped') {
            startBtn.style.display = 'block';
            pauseBtn.style.display = 'none';
        } else if (is_paused) {
            startBtn.style.display = 'block';
            pauseBtn.style.display = 'none';
        } else {
            startBtn.style.display = 'none';
            pauseBtn.style.display = 'block';
        }

        // サーキュラープログレス更新（progressは0.0～1.0）
        progressManager.setProgress(progress);
    }
}

const timerManager = new TimerManager();
