# ポモドーロタイマー Webアプリケーション アーキテクチャ設計書

## 📋 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [UI要件分析](#ui要件分析)
3. [タイマー仕様](#タイマー仕様)
4. [全体アーキテクチャ](#全体アーキテクチャ)
5. [ディレクトリ構造](#ディレクトリ構造)
6. [バックエンド設計](#バックエンド設計)
7. [フロントエンド設計](#フロントエンド設計)
8. [テスト性を考慮した設計](#テスト性を考慮した設計)
9. [API仕様](#api仕様)
10. [実装フェーズ](#実装フェーズ)

---

## プロジェクト概要

**プロジェクト名**: ポモドーロタイマー Webアプリケーション

**目的**: ポモドーロ・テクニックに基づいた集中力管理ツールの提供

**技術スタック**:
- バックエンド: Flask（Python）
- フロントエンド: HTML5 / CSS3 / Vanilla JavaScript
- データ永続化: JSON（ローカルファイル）
- テストフレームワーク: pytest

**主な特徴**:
- 柔軟な時間設定（5～99分）
- リアルタイム進捗表示（サーキュラープログレスバー）
- 本日のセッション統計追跡
- テスト駆動開発に対応した設計

---

## UI要件分析

### UIモック構成要素

```
┌─────────────────────────────────────┐
│  ポモドーロタイマー            [- □ ×] │
├─────────────────────────────────────┤
│                                     │
│              作業中                  │
│                                     │
│         ┌─────────────────┐         │
│         │                 │         │
│         │    25:00        │ ◯       │ サーキュラープログレス
│         │                 │         │
│         └─────────────────┘         │
│                                     │
│      [開始]  [リセット]             │ アクションボタン
│                                     │
├─────────────────────────────────────┤
│         今日の進捗                   │
│                                     │
│  4        1時間40分                │
│  完了      集中時間                 │
└─────────────────────────────────────┘
```

### UI要素仕様

| 要素 | 型 | 機能 | 仕様 |
|------|-----|------|------|
| **タイマー表示** | 数値表示 | 残り時間の表示 | MM:SS 形式（例: 25:00） |
| **状態ラベル** | テキスト | セッション状態表示 | 「作業中」「休憩中」「停止中」 |
| **サーキュラープログレス** | 円形グラフ | 進捗度の可視化 | CSS / SVG で実装 |
| **開始ボタン** | 押下可能 | タイマー開始 / 再開 | 状態に応じてテキスト変更 |
| **リセットボタン** | 押下可能 | タイマーリセット | セッション初期化 |
| **セッション数** | カウンター | 本日完了数 | 動的更新 |
| **集中時間** | 時間表示 | 本日累計集中時間 | HH分形式（例: 1時間40分） |

---

## タイマー仕様

### 時間設定

```python
TIMER_CONFIG = {
    "work_min": 5,           # 作業時間（最小）
    "work_max": 99,          # 作業時間（最大）← 99分に上限確定
    "break_min": 1,          # 休憩時間（最小）
    "break_max": 99,         # 休憩時間（最大）
    "default_work": 25,      # デフォルト作業時間
    "default_break": 5,      # デフォルト休憩時間
    "long_break_minutes": 15,# 長休憩（4セッション後）
}
```

### 時間表示フォーマット

**統一フォーマット**: MM:SS（分:秒）

```javascript
// フォーマット関数
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// 表示例
formatTime(300);    // "05:00"（5分）
formatTime(1500);   // "25:00"（25分）
formatTime(3600);   // "60:00"（60分）
formatTime(5940);   // "99:00"（99分）
```

**選定理由**:
- 99分が上限により、MM:SS形式で完全に表現可能
- UI モックのそのまま採用
- フォントサイズ調整不要で、レイアウト安定

### タイマー状態遷移

```
初期状態
  │
  ├─ [開始] → 実行中（カウントダウン）
  │            │
  │            ├─ [一時停止] → 一時停止状態
  │            │               │
  │            │               ├─ [再開] → 実行中
  │            │               │
  │            │               └─ [リセット] → 初期状態
  │            │
  │            ├─ [リセット] → 初期状態
  │            │
  │            └─ セッション終了 → ブレイク状態
  │                            （自動遷移）
  │
  └─ [リセット] → 初期状態
```

### リセット機能の分類

| リセット種別 | 対象 | トリガー | 効果 |
|-------------|------|---------|------|
| **セッションリセット** | 現在のタイマー | [リセット]ボタン | タイマーを初期値にリセット |
| **設定リセット** | 作業時間・休憩時間 | 設定画面[リセット] | ユーザー設定を初期値に戻す |
| **統計リセット** | 今日の進捗 | 統計画面[統計をリセット] | 本日のセッション数・累計時間を削除（確認ダイアログ必須） |

---

## 全体アーキテクチャ

### レイヤー構成図

```
┌─────────────────────────────────────────────────────┐
│            ルート層（routes）                        │
│  ・Flask エンドポイント                             │
│  ・HTTP リクエスト処理                             │
│  ・JSON レスポンス生成                             │
└──────────────────┬──────────────────────────────────┘
                   │ 依存性注入
┌──────────────────▼──────────────────────────────────┐
│          サービス層（services）                     │
│  ・ビジネスロジック実装                            │
│  ・リポジトリへのアクセス                          │
│  ・データ整形・変換                               │
└──────────────────┬──────────────────────────────────┘
                   │ 依存性注入
┌──────────────────▼──────────────────────────────────┐
│           モデル層（models）                        │
│  ├─ Timer（Clock 抽象に依存）                      │
│  ├─ SessionManager（Repository に依存）           │
│  ├─ DailyStats（データコンテナ）                   │
│  ├─ TimerConfig（設定オブジェクト）                │
│  └─ 抽象インターフェース                           │
│      ├─ Clock（時間管理）                          │
│      └─ Repository（永続化）                       │
└─────────────────────────────────────────────────────┘

テスト層:
  ・MockClock: 時間経過の制御可能化
  ・InMemoryRepository: 永続化層の分離
  ・テスト用設定: 固定値テスト
```

### 依存性の流れ

```
routes/api.py
    ↓ (依存性注入)
services/timer_service.py
    ↓ (依存性注入)
models/timer.py + models/clock.py
    ↓
テスト環境では MockClock・InMemoryRepository を注入
```

---

## ディレクトリ構造

```
1.pomodoro/
├── app.py                          # Flask アプリケーション（エントリーポイント）
├── config.py                       # 設定管理（外部化）
│
├── models/                         # ドメインモデル層
│   ├── __init__.py
│   ├── timer.py                    # タイマーロジック（Clock 依存）
│   ├── session.py                  # セッション・統計管理（Repository 依存）
│   ├── clock.py                    # ⭐ Clock インターフェース＋実装
│   ├── repository.py               # ⭐ Repository インターフェース＋実装
│   └── config_model.py             # ⭐ 設定データモデル
│
├── services/                       # ビジネスロジック層
│   ├── __init__.py
│   ├── timer_service.py            # タイマーサービス（ロジック）
│   └── session_service.py          # セッションサービス（ロジック）
│
├── routes/                         # HTTP層
│   ├── __init__.py
│   ├── api.py                      # REST API エンドポイント
│   └── web.py                      # ページ描画
│
├── static/                         # 静的ファイル
│   ├── css/
│   │   ├── style.css               # グローバルスタイル
│   │   └── timer.css               # タイマー固有スタイル
│   └── js/
│       ├── main.js                 # 初期化＆イベント処理
│       ├── timer.js                # タイマー状態管理
│       ├── progress.js             # サーキュラープログレス描画
│       └── api.js                  # API通信抽象化
│
├── templates/
│   └── index.html                  # メインUI（HTML）
│
├── tests/                          # ⭐ テストスイート
│   ├── __init__.py
│   ├── conftest.py                 # pytest 共通設定＆フィクスチャ
│   ├── test_timer.py               # タイマー単体テスト
│   ├── test_session.py             # セッション単体テスト
│   ├── test_services/
│   │   ├── test_timer_service.py   # サービスレイヤーテスト
│   │   └── test_session_service.py
│   └── test_integration.py         # 統合テスト
│
├── pomodoro.png                    # UIモック(design reference)
├── architecture.md                 # このファイル
└── README.md
```

---

## バックエンド設計

### 1. モデル層（models/）

#### timer.py - タイマー実装

```python
from models.clock import Clock
from config import TimerConfig

class TimerState:
    WORK = "work"
    BREAK = "break"
    LONG_BREAK = "long_break"
    STOPPED = "stopped"

class PomodoroTimer:
    """
    ポモドーロタイマーの核となるロジック
    
    Clock インターフェースに依存することで、
    テスト時にシステム時刻を制御可能にする
    """
    
    def __init__(self, config: TimerConfig, clock: Clock):
        self.config = config
        self.clock = clock  # 依存性注入
        
        self.start_time = None
        self.paused_elapsed = 0
        self.state = TimerState.STOPPED
        self.is_paused = False
    
    def start(self) -> None:
        """タイマー開始"""
        self.start_time = self.clock.now()
        self.state = TimerState.WORK
        self.is_paused = False
    
    def pause(self) -> None:
        """一時停止"""
        if not self.is_paused:
            self.paused_elapsed = self.get_elapsed()
            self.is_paused = True
    
    def resume(self) -> None:
        """再開"""
        if self.is_paused:
            self.start_time = self.clock.now() - self.paused_elapsed
            self.is_paused = False
    
    def reset(self) -> None:
        """リセット"""
        self.start_time = None
        self.paused_elapsed = 0
        self.state = TimerState.STOPPED
        self.is_paused = False
    
    def get_elapsed(self) -> int:
        """経過秒数を取得"""
        if self.start_time is None:
            return 0
        return int(self.clock.now() - self.start_time)
    
    def get_remaining(self) -> int:
        """残り秒数を取得"""
        duration = self.config.work_minutes * 60  # 秒単位
        remaining = duration - self.get_elapsed()
        return max(0, remaining)
    
    def get_progress(self) -> float:
        """進捗率（0.0～1.0）を取得"""
        duration = self.config.work_minutes * 60
        elapsed = self.get_elapsed()
        return min(1.0, elapsed / duration)
    
    def is_completed(self) -> bool:
        """セッション完了か判定"""
        return self.get_remaining() == 0
    
    def get_display_time(self) -> str:
        """表示用時間文字列を取得（MM:SS形式）"""
        remaining = self.get_remaining()
        mins = remaining // 60
        secs = remaining % 60
        return f"{mins:02d}:{secs:02d}"
```

#### clock.py - 時間抽象化（テスト性向上）

```python
from abc import ABC, abstractmethod
import time

class Clock(ABC):
    """時間アクセスの抽象インターフェース"""
    
    @abstractmethod
    def now(self) -> float:
        """現在の UNIX タイムスタンプを返す"""
        pass

class RealClock(Clock):
    """本番用：実際のシステム時刻を返す"""
    
    def now(self) -> float:
        return time.time()

class MockClock(Clock):
    """テスト用：時刻を制御可能"""
    
    def __init__(self, initial_time: float = 0.0):
        self._current_time = initial_time
    
    def now(self) -> float:
        return self._current_time
    
    def advance(self, seconds: float) -> None:
        """テスト用：時刻を進める"""
        self._current_time += seconds
```

#### session.py - セッション・統計管理

```python
from datetime import datetime
from models.repository import SessionRepository
from dataclasses import dataclass, field
from typing import List

@dataclass
class SessionRecord:
    """完了したセッションの記録"""
    duration: int  # 秒単位
    timestamp: float
    state: str  # "work" or "break"

@dataclass
class DailyStats:
    """本日の統計情報"""
    completed_sessions: int = 0
    total_focus_seconds: int = 0
    session_history: List[SessionRecord] = field(default_factory=list)

class SessionManager:
    """
    セッション・統計のビジネスロジック管理
    
    Repository パターンで永続化を分離
    テスト時には InMemoryRepository を注入
    """
    
    def __init__(self, repository: SessionRepository):
        self.repository = repository
        self.today_stats = DailyStats()
    
    def complete_session(self, duration: int, state: str = "work") -> None:
        """セッション完了を記録"""
        self.today_stats.completed_sessions += 1
        self.today_stats.total_focus_seconds += duration
        
        record = SessionRecord(
            duration=duration,
            timestamp=datetime.now().timestamp(),
            state=state
        )
        self.today_stats.session_history.append(record)
    
    def get_today_stats(self) -> dict:
        """本日の統計を辞書形式で取得"""
        focus_minutes = self.today_stats.total_focus_seconds // 60
        focus_hours = focus_minutes // 60
        focus_mins = focus_minutes % 60
        
        if focus_hours > 0:
            focus_display = f"{focus_hours}時間{focus_mins}分"
        else:
            focus_display = f"{focus_mins}分"
        
        return {
            "completed_sessions": self.today_stats.completed_sessions,
            "total_focus_seconds": self.today_stats.total_focus_seconds,
            "focus_display": focus_display,
            "session_history": [
                {
                    "duration": r.duration,
                    "timestamp": r.timestamp,
                    "state": r.state
                }
                for r in self.today_stats.session_history
            ]
        }
    
    def reset(self) -> None:
        """統計をリセット"""
        self.today_stats = DailyStats()
    
    def save(self) -> None:
        """永続化層に保存"""
        self.repository.save(self.today_stats)
```

#### repository.py - 永続化抽象（テスト性向上）

```python
from abc import ABC, abstractmethod
import json
from pathlib import Path
from models.session import DailyStats

class SessionRepository(ABC):
    """永続化層の抽象インターフェース"""
    
    @abstractmethod
    def save(self, stats: DailyStats) -> None:
        pass
    
    @abstractmethod
    def load(self) -> DailyStats:
        pass

class InMemoryRepository(SessionRepository):
    """テスト用：メモリに保存"""
    
    def __init__(self):
        self.data = {}
    
    def save(self, stats: DailyStats) -> None:
        self.data['today'] = stats
    
    def load(self) -> DailyStats:
        return self.data.get('today', DailyStats())

class FileRepository(SessionRepository):
    """本番用：JSON ファイルに保存"""
    
    def __init__(self, file_path: str = "data/session_stats.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save(self, stats: DailyStats) -> None:
        data = {
            "completed_sessions": stats.completed_sessions,
            "total_focus_seconds": stats.total_focus_seconds,
            "session_history": [
                {
                    "duration": r.duration,
                    "timestamp": r.timestamp,
                    "state": r.state
                }
                for r in stats.session_history
            ]
        }
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load(self) -> DailyStats:
        if not self.file_path.exists():
            return DailyStats()
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stats = DailyStats(
            completed_sessions=data.get('completed_sessions', 0),
            total_focus_seconds=data.get('total_focus_seconds', 0)
        )
        return stats
```

#### config_model.py - 設定管理

```python
from dataclasses import dataclass

@dataclass
class TimerConfig:
    """タイマー設定オブジェクト"""
    work_minutes: int = 25
    break_minutes: int = 5
    min_minutes: int = 5
    max_minutes: int = 99
    
    def validate(self) -> bool:
        """設定値のバリデーション"""
        return (self.min_minutes <= self.work_minutes <= self.max_minutes and
                self.min_minutes <= self.break_minutes <= self.max_minutes)
    
    def reset(self) -> None:
        """デフォルト設定にリセット"""
        self.work_minutes = 25
        self.break_minutes = 5
```

### 2. サービス層（services/）

```python
# services/timer_service.py
from models.timer import PomodoroTimer
from models.clock import Clock
from config_model import TimerConfig

class TimerService:
    """タイマーへの公開インターフェース（ビジネスロジック）"""
    
    def __init__(self, timer: PomodoroTimer):
        self.timer = timer
    
    def start(self) -> dict:
        """タイマー開始"""
        self.timer.start()
        return self._get_status()
    
    def pause(self) -> dict:
        """一時停止"""
        self.timer.pause()
        return self._get_status()
    
    def resume(self) -> dict:
        """再開"""
        self.timer.resume()
        return self._get_status()
    
    def reset(self) -> dict:
        """リセット"""
        self.timer.reset()
        return self._get_status()
    
    def get_status(self) -> dict:
        """ステータス取得"""
        return self._get_status()
    
    def _get_status(self) -> dict:
        """現在のステータスを辞書化"""
        return {
            "remaining_seconds": self.timer.get_remaining(),
            "display_time": self.timer.get_display_time(),
            "progress_percent": self.timer.get_progress() * 100,
            "state": self.timer.state,
            "is_paused": self.timer.is_paused,
            "is_completed": self.timer.is_completed()
        }
```

### 3. ルート層（routes/）

```python
# routes/api.py
from flask import Blueprint, jsonify, request
from services.timer_service import TimerService
from services.session_service import SessionService

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 依存性注入（app.py で行う）
timer_service: TimerService = None
session_service: SessionService = None

def init_api(app, ts: TimerService, ss: SessionService):
    """API の初期化（依存性注入）"""
    global timer_service, session_service
    timer_service = ts
    session_service = ss
    app.register_blueprint(api_bp)

# タイマー API
@api_bp.route('/timer/start', methods=['POST'])
def start_timer():
    """タイマー開始"""
    status = timer_service.start()
    return jsonify(status), 200

@api_bp.route('/timer/pause', methods=['POST'])
def pause_timer():
    """タイマー一時停止"""
    status = timer_service.pause()
    return jsonify(status), 200

@api_bp.route('/timer/resume', methods=['POST'])
def resume_timer():
    """タイマー再開"""
    status = timer_service.resume()
    return jsonify(status), 200

@api_bp.route('/timer/reset', methods=['POST'])
def reset_timer():
    """タイマーリセット"""
    status = timer_service.reset()
    return jsonify(status), 200

@api_bp.route('/timer/status', methods=['GET'])
def get_timer_status():
    """タイマー状態取得"""
    status = timer_service.get_status()
    return jsonify(status), 200

# セッション API
@api_bp.route('/session/today', methods=['GET'])
def get_today_stats():
    """本日の統計取得"""
    stats = session_service.get_today_stats()
    return jsonify(stats), 200

@api_bp.route('/session/complete', methods=['POST'])
def complete_session():
    """セッション完了記録"""
    data = request.get_json()
    duration = data.get('duration', 0)
    session_service.complete_session(duration)
    return jsonify({"status": "success"}), 200

@api_bp.route('/session/reset-today', methods=['POST'])
def reset_today():
    """本日の統計リセット（確認必須）"""
    data = request.get_json()
    if data.get('confirmed'):
        session_service.reset()
        return jsonify({"status": "success", "message": "統計をリセットしました"}), 200
    return jsonify({"error": "確認されていません"}), 400
```

---

## フロントエンド設計

### HTML テンプレート（templates/index.html）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ポモドーロタイマー</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/timer.css') }}">
</head>
<body>
    <div class="container">
        <!-- ヘッダー -->
        <header class="header">
            <h1>ポモドーロタイマー</h1>
            <button id="settingsBtn" class="settings-btn">⚙️</button>
        </header>

        <!-- タイマーセクション -->
        <section class="timer-section">
            <div class="state-label" id="stateLabel">作業中</div>

            <!-- サーキュラープログレス -->
            <div class="progress-container">
                <svg class="progress-ring" viewBox="0 0 200 200">
                    <circle class="progress-ring__background" cx="100" cy="100" r="90"></circle>
                    <circle class="progress-ring__circle" cx="100" cy="100" r="90"></circle>
                </svg>
                <div class="timer-display" id="timerDisplay">25:00</div>
            </div>

            <!-- アクションボタン -->
            <div class="button-group">
                <button id="startBtn" class="btn btn-primary">開始</button>
                <button id="pauseBtn" class="btn btn-primary" style="display: none;">一時停止</button>
                <button id="resetBtn" class="btn btn-outline">リセット</button>
            </div>
        </section>

        <!-- 今日の進捗セクション -->
        <section class="stats-section">
            <h2>今日の進捗</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="sessionsCompleted">0</div>
                    <div class="stat-label">完了</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="focusTime">0分</div>
                    <div class="stat-label">集中時間</div>
                </div>
            </div>
        </section>
    </div>

    <script src="{{ url_for('static', filename='js/api.js') }}"></script>
    <script src="{{ url_for('static', filename='js/timer.js') }}"></script>
    <script src="{{ url_for('static', filename='js/progress.js') }}"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

### JavaScript 実装概要

#### api.js - API 通信抽象化

```javascript
// static/js/api.js
class APIClient {
    async post(endpoint, data = {}) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }

    async get(endpoint) {
        const response = await fetch(endpoint);
        return response.json();
    }
}

const api = new APIClient();
```

#### timer.js - タイマー状態管理

```javascript
// static/js/timer.js
class TimerManager {
    constructor() {
        this.status = null;
        this.pollInterval = null;
    }

    async start() {
        this.status = await api.post('/api/timer/start');
        this.startPolling();
    }

    async pause() {
        this.status = await api.post('/api/timer/pause');
    }

    async resume() {
        this.status = await api.post('/api/timer/resume');
    }

    async reset() {
        this.status = await api.post('/api/timer/reset');
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
        const { display_time, progress_percent, state, is_paused } = this.status;
        
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

        // サーキュラープログレス更新
        progressManager.setProgress(progress_percent / 100);
    }
}

const timerManager = new TimerManager();
```

#### progress.js - サーキュラープログレス描画

```javascript
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
```

#### main.js - 初期化＆イベント処理

```javascript
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
    const stats = await api.get('/api/session/today');
    document.getElementById('sessionsCompleted').textContent = 
        stats.completed_sessions;
    document.getElementById('focusTime').textContent = 
        stats.focus_display;
}
```

### CSS 実装概要

```css
/* static/css/timer.css */

.progress-container {
    position: relative;
    width: 200px;
    height: 200px;
    margin: 2rem auto;
}

.progress-ring {
    transform: rotate(-90deg);
    width: 100%;
    height: 100%;
}

.progress-ring__background {
    fill: none;
    stroke: #e0e0e0;
    stroke-width: 8;
}

.progress-ring__circle {
    fill: none;
    stroke: #5b6ef5;
    stroke-width: 8;
    stroke-linecap: round;
    transition: stroke-dashoffset 0.35s ease-out;
}

.timer-display {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 3.5rem;
    font-weight: bold;
    font-variant-numeric: tabular-nums;
    font-family: 'Courier New', monospace;
}

.btn {
    padding: 0.75rem 2rem;
    border-radius: 50px;
    border: none;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-primary {
    background: linear-gradient(135deg, #5b6ef5, #4c5ee8);
    color: white;
}

.btn-outline {
    border: 2px solid #5b6ef5;
    color: #5b6ef5;
    background: transparent;
}

.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.stat-card {
    background: #f5f5f5;
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
}

.stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: #5b6ef5;
}

.stat-label {
    color: #666;
    margin-top: 0.5rem;
}
```

---

## テスト性を考慮した設計

### テスト対象とテスト方法

| コンポーネント | テスト種別 | テスト対象 | モック化 |
|-------------|---------|---------|--------|
| **Timer** | 単体 | get_remaining(), get_progress() | Clock |
| **SessionManager** | 単体 | complete_session(), reset() | Repository |
| **TimerService** | 単体 | start(), pause(), resume() | Timer |
| **API エンドポイント** | 統合 | HTTP レスポンス | TimerService, SessionService |

### テストダブル構成

```python
# models/clock.py
class MockClock(Clock):
    """テスト用クロック（時間を手動制御）"""
    def __init__(self, initial_time=0.0):
        self._current_time = initial_time
    
    def now(self):
        return self._current_time
    
    def advance(self, seconds):
        """テスト用：時刻を進める"""
        self._current_time += seconds

# models/repository.py
class InMemoryRepository(SessionRepository):
    """テスト用リポジトリ（メモリ保存）"""
    def __init__(self):
        self.data = {}
    
    def save(self, stats):
        self.data['today'] = stats
    
    def load(self):
        return self.data.get('today', DailyStats())
```

### テストスイート構成

```
tests/
├── conftest.py              # フィクスチャ定義
├── test_timer.py            # タイマー単体テスト
├── test_session.py          # セッション単体テスト
├── test_services/
│   ├── test_timer_service.py
│   └── test_session_service.py
└── test_integration.py      # 統合テスト
```

**テスト実行例:**
```bash
# すべてのテストを実行
pytest tests/

# 単体テストのみ
pytest tests/test_timer.py -v

# 特定のテストのみ
pytest tests/test_timer.py::test_timer_countdown -v

# カバレッジ測定
pytest --cov=models tests/
```

---

## API 仕様

### タイマー API

#### POST /api/timer/start
**説明**: タイマーを開始する

**レスポンス:**
```json
{
  "remaining_seconds": 1500,
  "display_time": "25:00",
  "progress_percent": 0.0,
  "state": "work",
  "is_paused": false,
  "is_completed": false
}
```

#### POST /api/timer/pause
**説明**: タイマーを一時停止する

**レスポンス**: /start と同じ（state は変更なし）

#### POST /api/timer/resume
**説明**: 一時停止中のタイマーを再開する

**レスポンス**: /start と同じ

#### POST /api/timer/reset
**説明**: タイマーをリセット（初期表示に戻す）

**レスポンス**:
```json
{
  "remaining_seconds": 1500,
  "display_time": "25:00",
  "progress_percent": 0.0,
  "state": "stopped",
  "is_paused": false,
  "is_completed": false
}
```

#### GET /api/timer/status
**説明**: 現在のタイマー状態を取得（ポーリング用）

**レスポンス**: /start と同じ

### セッション API

#### GET /api/session/today
**説明**: 本日のセッション統計を取得

**レスポンス:**
```json
{
  "completed_sessions": 4,
  "total_focus_seconds": 6000,
  "focus_display": "1時間40分",
  "session_history": [
    {
      "duration": 1500,
      "timestamp": 1677123456.789,
      "state": "work"
    }
  ]
}
```

#### POST /api/session/complete
**説明**: セッション完了を記録

**リクエスト:**
```json
{
  "duration": 1500
}
```

**レスポンス:**
```json
{
  "status": "success"
}
```

#### POST /api/session/reset-today
**説明**: 本日の統計をリセット（確認必須）

**リクエスト:**
```json
{
  "confirmed": true
}
```

**レスポンス:**
```json
{
  "status": "success",
  "message": "統計をリセットしました"
}
```

---

## 実装フェーズ

### Phase 1: バックエンド基本（1～2日）

**目標**: タイマーロジックの実装・検証

**実装項目**:
- [ ] models/clock.py（RealClock, MockClock）
- [ ] models/timer.py（PomodoroTimer）
- [ ] models/session.py（SessionManager, DailyStats）
- [ ] models/repository.py（インターフェース + 実装）
- [ ] config.py（TimerConfig）
- [ ] services/timer_service.py
- [ ] routes/api.py（タイマー API）

**テスト**:
- [ ] test_timer.py: タイマーのカウントダウンテスト（MockClock 使用）
- [ ] test_session.py: セッション記録テスト（InMemoryRepository 使用）

### Phase 2: フロントエンド基本（1～2日）

**目標**: UI レイアウト完成・API 連携

**実装項目**:
- [ ] templates/index.html（レイアウト）
- [ ] static/css/style.css・timer.css（スタイリング）
- [ ] static/js/api.js（API クライアント）
- [ ] static/js/timer.js（タイマー管理）
- [ ] static/js/main.js（イベント処理）

**テスト**:
- [ ] ブラウザで手動テスト

### Phase 3: タイマー機能統合（1日）

**目標**: リアルタイムタイマー動作確認

**実装項目**:
- [ ] static/js/progress.js（サーキュラープログレス）
- [ ] ポーリングロジック実装（1秒ごと更新）

**テスト**:
- [ ] UI 更新タイミング確認
- [ ] 時間精度確認

### Phase 4: 統計・リセット機能（1日）

**目標**: 完全な機能実装

**実装項目**:
- [ ] POST /api/session/complete エンドポイント
- [ ] POST /api/session/reset-today エンドポイント
- [ ] 統計表示とリセット UI実装
- [ ] 確認ダイアログ実装

**テスト**:
- [ ] test_integration.py（統合テスト）
- [ ] エンドツーエンドテスト

### Phase 5: 設定管理・最適化（1日）

**目標**: 時間設定変更機能、パフォーマンス最適化

**実装項目**:
- [ ] POST /api/config/update エンドポイント
- [ ] 設定 UI（スライダー / 入力フォーム）
- [ ] LocalStorage で設定保存
- [ ] パフォーマンス最適化

**テスト**:
- [ ] 設定バリデーションテスト
- [ ] ロードテスト

---

## 備考

### 開発環境構築

```bash
# 依存パッケージのインストール
pip install flask pytest pytest-cov

# テスト実行
pytest tests/ -v

# カバレッジ評価
pytest --cov=models --cov=services tests/
```

### 設計の拡張性

このアーキテクチャは以下への拡張が容易です：
- **データベース統合**: Repository パターンで FileRepository → SQLAlchemy に置換
- **マルチユーザー対応**: ユーザーセッション層を追加
- **通知機能**: セッション完了時に音声・通知を追加
- **統計分析**: セッン履歴からレポート生成

---

**文書作成日**: 2026年2月24日  
**バージョン**: 1.0
