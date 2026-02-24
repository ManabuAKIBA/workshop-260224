/**
 * CircularProgressManager - サーキュラープログレスバーの管理
 * SVGのstroke-dashoffsetを動的に更新して進捗を視覚化
 */
class CircularProgressManager {
    constructor(circleSelector = '.progress-ring__circle') {
        this.circle = document.querySelector(circleSelector);
        
        if (!this.circle) {
            console.error('Progress circle element not found');
            return;
        }
        
        // 円の半径を取得（SVGのr属性）
        const radius = parseFloat(this.circle.getAttribute('r'));
        
        // 円周の長さを計算: 2πr
        this.circumference = 2 * Math.PI * radius;
        
        // stroke-dasharray と stroke-dashoffset を初期化
        this.circle.style.strokeDasharray = `${this.circumference} ${this.circumference}`;
        this.circle.style.strokeDashoffset = this.circumference; // 初期状態は0%（円が見えない）
    }

    /**
     * 進捗率を設定
     * @param {number} progress - 進捗率（0.0～1.0）
     */
    setProgress(progress) {
        if (!this.circle) {
            return;
        }
        
        // 進捗率を0.0～1.0の範囲に制限
        const normalizedProgress = Math.max(0, Math.min(1, progress));
        
        // stroke-dashoffsetを計算
        // 進捗0% → offset = circumference（円が見えない）
        // 進捗100% → offset = 0（円が完全に表示）
        const offset = this.circumference * (1 - normalizedProgress);
        
        // CSSでアニメーションさせる
        this.circle.style.strokeDashoffset = offset;
    }

    /**
     * 進捗をリセット（0%に戻す）
     */
    reset() {
        this.setProgress(0);
    }
}
