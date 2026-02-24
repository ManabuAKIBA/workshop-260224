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
            // ボタンのテキストで開始か再開かを判定
            if (startBtn.textContent === '再開') {
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
            // リセット後は開始ボタンのテキストを「開始」に戻す
            if (startBtn) {
                startBtn.textContent = '開始';
            }
        });
    }

    // 初期状態を取得して表示
    timerManager.getStatus();
});
