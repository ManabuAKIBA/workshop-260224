/**
 * メインアプリケーション
 * 
 * UI イベントと統計表示の管理
 */

// グローバル変数
let apiClient;
let timerManager;

/**
 * アプリケーションの初期化
 */
function initApp() {
    console.log('Initializing app...');
    
    // API クライアントとタイマーマネージャーを初期化
    apiClient = new APIClient();
    timerManager = new TimerManager(apiClient);
    
    // イベントリスナーを設定
    setupEventListeners();
    
    // 初期表示を更新
    updateDisplay();
    updateStats();
    
    console.log('App initialized');
}

/**
 * イベントリスナーを設定
 */
function setupEventListeners() {
    // 開始ボタン
    const startBtn = document.getElementById('startBtn');
    if (startBtn) {
        startBtn.addEventListener('click', handleStart);
    }
    
    // リセットボタン
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', handleReset);
    }
    
    // タイマー更新イベント
    document.addEventListener('timer-update', handleTimerUpdate);
    
    // 統計更新イベント
    document.addEventListener('stats-update', updateStats);
}

/**
 * 開始ボタンのクリックハンドラー
 */
async function handleStart() {
    try {
        await timerManager.start();
        updateDisplay();
    } catch (error) {
        console.error('Error starting timer:', error);
        alert('タイマーの開始に失敗しました');
    }
}

/**
 * リセットボタンのクリックハンドラー
 */
function handleReset() {
    // ポーリングを停止
    timerManager.stopPolling();
    
    // 表示をリセット
    updateTimerDisplay('25:00');
    updateStateLabel('待機中');
}

/**
 * タイマー更新イベントのハンドラー
 * 
 * @param {CustomEvent} event - タイマー更新イベント
 */
function handleTimerUpdate(event) {
    const status = event.detail;
    updateTimerDisplay(status.display_time);
    updateStateLabel(getStateLabel(status.state));
}

/**
 * タイマー表示を更新
 * 
 * @param {string} time - 表示する時間（MM:SS形式）
 */
function updateTimerDisplay(time) {
    const display = document.getElementById('timerDisplay');
    if (display) {
        display.textContent = time;
    }
}

/**
 * 状態ラベルを更新
 * 
 * @param {string} label - 表示するラベル
 */
function updateStateLabel(label) {
    const stateLabel = document.getElementById('stateLabel');
    if (stateLabel) {
        stateLabel.textContent = label;
    }
}

/**
 * 状態コードから日本語ラベルを取得
 * 
 * @param {string} state - 状態コード（work/break/stopped等）
 * @returns {string} 日本語ラベル
 */
function getStateLabel(state) {
    const labels = {
        'work': '作業中',
        'break': '休憩中',
        'long_break': '長休憩中',
        'stopped': '待機中'
    };
    return labels[state] || '待機中';
}

/**
 * 表示を更新（初期化時やリセット時に呼ばれる）
 */
async function updateDisplay() {
    try {
        const status = await timerManager.getStatus();
        updateTimerDisplay(status.display_time);
        updateStateLabel(getStateLabel(status.state));
    } catch (error) {
        console.error('Error updating display:', error);
    }
}

/**
 * 統計を更新
 */
async function updateStats() {
    try {
        const stats = await apiClient.get('/session/today');
        
        // 完了セッション数を更新
        const sessionsElement = document.getElementById('sessionsCompleted');
        if (sessionsElement) {
            sessionsElement.textContent = stats.completed_work_sessions;
        }
        
        // 集中時間を更新
        const focusTimeElement = document.getElementById('focusTime');
        if (focusTimeElement) {
            focusTimeElement.textContent = `${stats.total_work_minutes}分`;
        }
        
        console.log('Stats updated:', stats);
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// DOMContentLoadedイベントでアプリを初期化
document.addEventListener('DOMContentLoaded', initApp);
