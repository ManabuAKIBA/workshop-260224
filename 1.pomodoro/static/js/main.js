/**
 * メイン初期化スクリプト
 * DOMロード完了後にイベントリスナーを設定
 */
document.addEventListener('DOMContentLoaded', () => {
    // イベントリスナー設定
    const startBtn = document.getElementById('startBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const resetBtn = document.getElementById('resetBtn');

    if (startBtn) {
        startBtn.addEventListener('click', async () => {
            // タイマーの状態に基づいて開始/再開を判断
            if (timerManager.status && timerManager.status.is_paused) {
                await timerManager.resume();
            } else {
                await timerManager.start();
            }
        });
    }

    if (pauseBtn) {
        pauseBtn.addEventListener('click', async () => {
            await timerManager.pause();
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            await timerManager.reset();
        });
    }

    // 初期状態取得
    timerManager.getStatus();
});
