/**
 * メインJavaScriptファイル
 * リセットボタンのイベントハンドラーを管理
 */

document.addEventListener('DOMContentLoaded', function() {
    // リセットボタン
    const resetBtn = document.getElementById('resetBtn');
    
    // リセットボタンのイベントハンドラー
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            // 確認ダイアログを表示
            if (confirm('本日の統計をリセットしますか？\nこの操作は取り消せません。')) {
                // リセットAPIを呼び出し
                fetch('/api/session/reset-today', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // 統計表示を0にリセット
                        const sessionsCompleted = document.getElementById('sessionsCompleted');
                        const focusTime = document.getElementById('focusTime');
                        
                        if (sessionsCompleted) {
                            sessionsCompleted.textContent = '0';
                        }
                        if (focusTime) {
                            focusTime.textContent = '0分';
                        }
                        
                        alert('統計をリセットしました');
                    }
                })
                .catch(error => {
                    console.error('リセットエラー:', error);
                    alert('統計のリセットに失敗しました');
                });
            }
        });
    }
});
