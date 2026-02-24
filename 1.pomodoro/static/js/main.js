/**
 * メイン初期化スクリプト
 * 
 * イベントハンドラーの設定とアプリケーションの初期化を行う
 */

document.addEventListener('DOMContentLoaded', () => {
    // 開始/再開ボタンのイベントリスナー
    const startBtn = document.getElementById('startBtn');
    if (startBtn) {
        startBtn.addEventListener('click', async () => {
            // 現在の状態で開始か再開かを判定
            if (timerManager.status && timerManager.status.is_paused) {
                await timerManager.resume();
            } else {
                await timerManager.start();
            }
        });
    }

    // 一時停止ボタンのイベントリスナー
    const pauseBtn = document.getElementById('pauseBtn');
    if (pauseBtn) {
        pauseBtn.addEventListener('click', async () => {
            await timerManager.pause();
        });
    }

    // リセットボタンのイベントリスナー
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            await timerManager.reset();
        });
    }

    // 初期状態を取得して表示
    timerManager.getStatus();
});
