// static/js/progress.js
class CircularProgressManager {
    constructor() {
        this.circle = document.querySelector('.progress-ring__circle');
        this.radius = this.circle.r.baseVal.value;
        this.circumference = 2 * Math.PI * this.radius;
        
        this.circle.style.strokeDasharray = this.circumference;
        this.circle.style.strokeDashoffset = this.circumference;
    }

    setProgress(progress) {
        // progress: 0.0 ～ 1.0
        const offset = this.circumference * (1 - progress);
        this.circle.style.strokeDashoffset = offset;
    }
}

const progressManager = new CircularProgressManager();
