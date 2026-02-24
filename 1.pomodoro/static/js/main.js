/**
 * main.js - アプリケーションのエントリーポイント
 * 各コンポーネントの初期化とイベントハンドラーの設定
 */

// グローバル変数
let apiClient;
let progressManager;
let timerManager;

/**
 * アプリケーション初期化
 */
function initializeApp() {
    // 各マネージャーを初期化
    apiClient = new APIClient();
    progressManager = new CircularProgressManager('.progress-ring__circle');
    timerManager = new TimerManager(apiClient, progressManager);
    
    // イベントリスナーを設定
    setupEventListeners();
    
    console.log('Pomodoro Timer initialized');
}

/**
 * イベントリスナーを設定
 */
function setupEventListeners() {
    const startBtn = document.getElementById('startBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const resetBtn = document.getElementById('resetBtn');
    
    // 開始ボタン
    if (startBtn) {
        startBtn.addEventListener('click', async () => {
            await timerManager.start();
        });
    }
    
    // 一時停止ボタン（将来的に実装）
    if (pauseBtn) {
        pauseBtn.addEventListener('click', async () => {
            // await timerManager.pause();
            console.log('Pause functionality not yet implemented');
        });
    }
    
    // リセットボタン
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            await timerManager.reset();
        });
    }
}

// DOMContentLoadedイベントでアプリケーションを初期化
document.addEventListener('DOMContentLoaded', initializeApp);
