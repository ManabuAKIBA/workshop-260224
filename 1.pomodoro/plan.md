# ポモドーロタイマー 段階的実装計画

**作成日**: 2026年2月24日  
**目標**: テスト駆動開発（TDD）と動作確認を重視した段階的実装  
**完成予定時間**: 8時間（MVP）+ 2時間（テスト整備）= 10時間

---

## 📊 実装時間サマリー

| ステップ | 内容 | 所要時間 | 累計時間 |
|---------|------|---------|---------|
| 1 | 環境構築 | 30分 | 30分 |
| 2 | タイマーコア（TDD） | 1時間 | 1.5時間 |
| 3 | セッション管理（TDD） | 1時間 | 2.5時間 |
| 4 | タイマーAPI | 1時間 | 3.5時間 |
| 5 | 基本UI | 1時間 | 4.5時間 |
| 6 | UI連携 | 1時間 | 5.5時間 |
| 7 | リアルタイム更新 | 30分 | 6時間 |
| 8 | プログレスバー | 30分 | 6.5時間 |
| 9 | セッション統計 | 1時間 | 7.5時間 |
| 10 | リセット機能 | 30分 | 8時間 |
| **MVP完成** | **—** | **—** | **8時間** |
| 11 | テスト整備 | 2時間 | 10時間 |

---

## 🎯 ステップ1: 最小限の動作環境構築

**目標**: "Hello World"レベルでFlaskアプリが起動することを確認  
**所要時間**: 30分

### 実装内容

- [ ] ディレクトリ構造の作成
  ```
  1.pomodoro/
  ├── models/
  ├── services/
  ├── routes/
  ├── static/
  │   ├── css/
  │   └── js/
  ├── templates/
  └── tests/
  ```
- [ ] 各ディレクトリに`__init__.py`を配置
- [ ] 基本的な`app.py`の実装（Flask初期化のみ）
- [ ] `templates/index.html`の基本レイアウト（静的なHTML）
- [ ] `routes/web.py`でルートページ描画

### 確認方法

```bash
# Flask起動
python app.py

# ブラウザで確認
# http://localhost:5000 にアクセスして画面表示を確認
```

### 成功条件

- ✅ ブラウザで画面が表示される
- ✅ エラーが発生しない

---

## 🔧 ステップ2: Clock抽象化とタイマーコア（TDD）

**目標**: テスト可能なタイマーロジックの実装  
**所要時間**: 1時間

### 実装内容

- [ ] `models/clock.py`
  - `Clock`（抽象インターフェース）
  - `RealClock`（本番用：実際のシステム時刻）
  - `MockClock`（テスト用：制御可能な時刻）

- [ ] `models/timer.py`
  - `TimerState`（状態定義）
  - `PomodoroTimer`（タイマーロジック）
    - `start()` - タイマー開始
    - `pause()` - 一時停止
    - `resume()` - 再開
    - `reset()` - リセット
    - `get_remaining_seconds()` - 残り時間計算
    - `get_progress()` - 進捗率計算（0.0～1.0）
    - `is_completed()` - 完了判定

- [ ] `tests/test_timer.py`（テストファースト）
  - タイマー開始時の残り時間テスト
  - MockClockで時間を進めたときの動作テスト
  - 進捗率の計算テスト
  - 完了判定のテスト

### 確認方法

```bash
# テスト実行
pytest tests/test_timer.py -v

# すべてのテストが通ることを確認
```

### 成功条件

- ✅ すべてのテストがパスする
- ✅ MockClockでタイマーの動作を制御できる

---

## 💾 ステップ3: セッション管理とRepository（TDD）

**目標**: データ永続化の基盤構築  
**所要時間**: 1時間

### 実装内容

- [ ] `models/repository.py`
  - `SessionRepository`（抽象インターフェース）
  - `InMemoryRepository`（テスト用：メモリ保存）
  - `FileRepository`（本番用：JSON保存）

- [ ] `models/session.py`
  - `SessionRecord`（セッション記録データクラス）
  - `DailyStats`（本日の統計データクラス）
  - `SessionManager`（セッション管理ロジック）
    - `complete_session()` - セッション完了記録
    - `get_today_stats()` - 本日の統計取得
    - `reset_today()` - 本日の統計リセット

- [ ] `tests/test_session.py`（テストファースト）
  - セッション完了記録のテスト
  - 本日の統計計算のテスト
  - InMemoryRepositoryでの読み書きテスト

### 確認方法

```bash
# テスト実行
pytest tests/test_session.py -v

# すべてのテストが通ることを確認
```

### 成功条件

- ✅ すべてのテストがパスする
- ✅ InMemoryRepositoryでデータの永続化ができる

---

## 🌐 ステップ4: タイマーAPI（最小構成）

**目標**: バックエンドAPIの動作確認  
**所要時間**: 1時間

### 実装内容

- [ ] `models/config_model.py`
  - `TimerConfig`（設定データクラス）

- [ ] `services/timer_service.py`
  - `TimerService`（タイマーのビジネスロジック）
    - `start()` - タイマー開始
    - `get_status()` - 現在の状態取得
    - （pause/resume/resetは次のステップで追加）

- [ ] `routes/api.py`
  - `POST /api/timer/start` - タイマー開始
  - `GET /api/timer/status` - タイマー状態取得

- [ ] `app.py`の完成
  - Flask初期化
  - 依存性注入（RealClock, FileRepository）
  - Blueprintの登録

### 確認方法

```bash
# ターミナル1: Flask起動
python app.py

# ターミナル2: curlでAPIテスト
curl -X POST http://localhost:5000/api/timer/start
curl http://localhost:5000/api/timer/status
```

### 成功条件

- ✅ `/api/timer/start`でJSONレスポンスが返る
- ✅ `/api/timer/status`で残り時間が取得できる

---

## 🎨 ステップ5: フロントエンド基本UI（静的表示）

**目標**: UIレイアウトの完成（動作はまだ）  
**所要時間**: 1時間

### 実装内容

- [ ] `templates/index.html`
  - 完全なHTML構造
  - タイマー表示エリア
  - サーキュラープログレスのSVG
  - ボタン（開始、一時停止、リセット）
  - 統計表示エリア

- [ ] `static/css/style.css`
  - グローバルスタイル
  - レスポンシブレイアウト

- [ ] `static/css/timer.css`
  - タイマー固有スタイル
  - サーキュラープログレスのスタイル
  - ボタンのスタイル
  - アニメーション

### 確認方法

```bash
# Flask起動
python app.py

# ブラウザで確認
# http://localhost:5000 にアクセス
```

### 成功条件

- ✅ UIモック（pomodoro.png）と見た目が一致する
- ✅ レスポンシブレイアウトが機能する

---

## ⚡ ステップ6: タイマーUIの動的連携

**目標**: ボタンクリックでタイマーが動作  
**所要時間**: 1時間

### 実装内容

- [ ] `static/js/api.js`
  - `APIClient`クラス
    - `post()` - POST リクエスト
    - `get()` - GET リクエスト

- [ ] `static/js/timer.js`
  - `TimerManager`クラス
    - `start()` - タイマー開始
    - `pause()` - 一時停止
    - `resume()` - 再開
    - `reset()` - リセット
    - `updateDisplay()` - 画面更新

- [ ] `static/js/main.js`
  - イベントハンドラー（開始、一時停止、リセット）
  - 初期化処理

- [ ] `routes/api.py`に追加
  - `POST /api/timer/pause` - 一時停止
  - `POST /api/timer/resume` - 再開
  - `POST /api/timer/reset` - リセット

### 確認方法

```bash
# ブラウザで確認
# - 開始ボタンをクリック → 残り時間が表示される
# - コンソールでAPIレスポンスを確認
```

### 成功条件

- ✅ 開始ボタンで残り時間が表示される
- ✅ 一時停止・再開・リセットが動作する

---

## 🔄 ステップ7: リアルタイム更新（ポーリング）

**目標**: 1秒ごとに画面が更新される  
**所要時間**: 30分

### 実装内容

- [ ] `static/js/timer.js`に追加
  - ポーリングロジック（1秒ごとに`/api/timer/status`を呼び出し）
  - タイマー表示の自動更新
  - 状態ラベルの更新

### 確認方法

```bash
# ブラウザで確認
# - 開始後、自動的にカウントダウンが進む
# - ブラウザのタブを切り替えても正確に動作
```

### 成功条件

- ✅ タイマーが1秒ごとに更新される
- ✅ 残り時間が正確に減少する

---

## 📊 ステップ8: サーキュラープログレス

**目標**: 進捗が視覚的に分かる  
**所要時間**: 30分

### 実装内容

- [ ] `static/js/progress.js`
  - `CircularProgressManager`クラス
    - `setProgress()` - 進捗率に応じた円弧の描画
    - SVGの`stroke-dashoffset`を動的に更新

- [ ] `static/js/timer.js`に統合
  - タイマー更新時にプログレスバーも更新

### 確認方法

```bash
# ブラウザで確認
# - タイマー実行中に円が徐々に減っていく
# - 進捗が視覚的に分かる
```

### 成功条件

- ✅ 円形プログレスバーがスムーズにアニメーション
- ✅ 進捗率が正確に反映される

---

## 📈 ステップ9: セッション統計機能

**目標**: セッション完了時の記録と表示  
**所要時間**: 1時間

### 実装内容

- [ ] `services/session_service.py`
  - `SessionService`（セッションのビジネスロジック）
    - `complete_session()` - セッション完了記録
    - `get_today_stats()` - 本日の統計取得

- [ ] `routes/api.py`に追加
  - `GET /api/session/today` - 本日の統計取得
  - `POST /api/session/complete` - セッション完了記録

- [ ] `static/js/timer.js`に追加
  - タイマー完了時の自動記録処理

- [ ] `static/js/main.js`に追加
  - 統計表示の更新処理

### 確認方法

```bash
# ブラウザで確認
# - 25分のタイマー完了後、「完了セッション数」が1増える
# - 「集中時間」が25分増える
```

### 成功条件

- ✅ セッション完了時に統計が更新される
- ✅ 本日の統計が正しく表示される

---

## 🔧 ステップ10: リセット機能と完成

**目標**: すべての機能が揃う  
**所要時間**: 30分

### 実装内容

- [ ] `routes/api.py`に追加
  - `POST /api/session/reset-today` - 本日の統計リセット

- [ ] `static/js/main.js`に追加
  - 統計リセットボタンのイベントハンドラー
  - 確認ダイアログ（`confirm()`）

### 確認方法

```bash
# ブラウザで確認
# - 統計リセットボタンをクリック
# - 確認ダイアログが表示される
# - OKをクリックすると統計が0に戻る
```

### 成功条件

- ✅ 統計リセットが動作する
- ✅ 確認ダイアログが表示される

---

## 🎉 MVP完成（ここまでで8時間）

**達成内容:**
- ✅ タイマー機能の完全動作
- ✅ セッション統計の記録と表示
- ✅ リセット機能
- ✅ リアルタイム更新
- ✅ サーキュラープログレスバー

---

## 🧪 ステップ11: テスト整備

**目標**: 品質保証とリファクタリング  
**所要時間**: 2時間

### 実装内容

- [ ] `tests/conftest.py`
  - pytestフィクスチャの定義

- [ ] `tests/test_services/test_timer_service.py`
  - TimerServiceの単体テスト

- [ ] `tests/test_services/test_session_service.py`
  - SessionServiceの単体テスト

- [ ] `tests/test_integration.py`
  - APIエンドポイントの統合テスト
  - Flask TestClientを使用

- [ ] カバレッジ測定
  - 目標: 80%以上

- [ ] バグ修正とリファクタリング

### 確認方法

```bash
# すべてのテストを実行
pytest tests/ -v

# カバレッジ測定
pytest --cov=models --cov=services tests/

# カバレッジレポート
pytest --cov=models --cov=services --cov-report=html tests/
```

### 成功条件

- ✅ すべてのテストがパスする
- ✅ カバレッジが80%以上

---

## 🚀 ステップ12: 拡張機能（オプション）

以下は余裕があれば実装：

### 設定変更UI（1～2時間）
- [ ] `GET /api/config` - 現在の設定取得
- [ ] `POST /api/config/update` - 設定更新
- [ ] 設定画面のUI実装

### 長休憩機能（1時間）
- [ ] 4セッション後に15分休憩のロジック
- [ ] 長休憩モードの表示

### 音声通知（30分）
- [ ] セッション完了時の通知音
- [ ] Web Audio API の使用

### LocalStorage対応（1時間）
- [ ] ブラウザリロード時の状態復元
- [ ] 設定のローカル保存

---

## ✅ 実装の進め方

### 推奨プラクティス

1. **毎ステップでコミット**
   ```bash
   git add .
   git commit -m "ステップX: XXX機能の実装"
   ```

2. **テストファースト（ステップ2-3）**
   - テストを先に書く
   - 実装してテストをパスさせる

3. **動作確認を必ず**
   - 次のステップに進む前に動作確認
   - 問題があれば修正してから進む

4. **ステップ1-10でMVP完成**
   - 基本機能がすべて動く状態

5. **ステップ11で品質向上**
   - テストカバレッジとリファクタリング

### トラブルシューティング

- **Flask起動エラー**: `pip install flask`を実行
- **テストエラー**: `pip install pytest`を実行
- **ポート競合**: `app.py`の`port=5000`を別のポートに変更
- **CORS エラー**: 必要に応じて`flask-cors`を導入

---

## 📚 参照ドキュメント

- [architecture.md](architecture.md) - アーキテクチャ設計書
- [features.md](features.md) - 実装機能一覧
- [pomodoro.png](pomodoro.png) - UIモック

---

**最終更新日**: 2026年2月24日
