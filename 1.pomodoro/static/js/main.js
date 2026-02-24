// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    // イベントリスナー設定
    document.getElementById('startBtn').addEventListener('click', () => {
        timerManager.start();
    });

    document.getElementById('pauseBtn').addEventListener('click', () => {
        timerManager.pause();
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
        timerManager.reset();
    });

    // 初期状態取得
    timerManager.getStatus();
    
    // 統計表示更新
    updateStats();
});

async function updateStats() {
    try {
        const stats = await api.get('/api/session/today');
        document.getElementById('sessionsCompleted').textContent = 
            stats.completed_sessions;
        document.getElementById('focusTime').textContent = 
            stats.focus_display;
    } catch (error) {
        // 統計APIがまだ実装されていない場合はスキップ
        console.log('Stats API not yet implemented');
    }
}
