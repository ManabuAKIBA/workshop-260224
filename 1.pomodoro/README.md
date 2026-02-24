# ポモドーロタイマー Web アプリケーション

## 概要

ポモドーロ・テクニックに基づいた、シンプルで効果的な集中力管理ツールです。

## 特徴

- 📊 **リアルタイム進捗表示**: サーキュラープログレスバーで視覚的に進捗を確認
- ⏱️ **柔軟な時間設定**: 5～99分の範囲で作業時間・休憩時間をカスタマイズ可能
- 📈 **統計追跡**: 本日のセッション数と累計集中時間を自動記録
- 🧪 **テスト駆動開発**: 包括的なテストスイートによる高品質な実装

## 技術スタック

- **バックエンド**: Flask (Python)
- **フロントエンド**: HTML5 / CSS3 / Vanilla JavaScript
- **データ永続化**: JSON (ローカルファイル)
- **テストフレームワーク**: pytest

## プロジェクト構造

```
1.pomodoro/
├── app.py                    # Flask アプリケーション (エントリーポイント)
├── config.py                 # 設定管理
│
├── models/                   # ドメインモデル層
│   ├── timer.py             # タイマーロジック
│   ├── session.py           # セッション・統計管理
│   ├── clock.py             # 時間管理の抽象化
│   ├── repository.py        # データ永続化の抽象化
│   └── config_model.py      # 設定データモデル
│
├── services/                 # ビジネスロジック層
│   ├── timer_service.py     # タイマーサービス
│   └── session_service.py   # セッションサービス
│
├── routes/                   # HTTP層
│   ├── api.py               # REST API エンドポイント
│   └── web.py               # ページ描画
│
├── static/                   # 静的ファイル
│   ├── css/
│   └── js/
│
├── templates/                # HTML テンプレート
│   └── index.html
│
└── tests/                    # テストスイート
    ├── conftest.py
    ├── test_timer.py
    ├── test_session.py
    ├── test_services/
    └── test_integration.py
```

## セットアップ

### 前提条件

- Python 3.8 以上
- pip

### インストール

```bash
# 依存パッケージのインストール
pip install flask pytest pytest-cov

# データディレクトリの作成（自動作成されますが、手動でも可）
mkdir -p 1.pomodoro/data
```

## 使い方

### アプリケーションの起動

```bash
cd 1.pomodoro
python app.py
```

ブラウザで http://localhost:5000 にアクセスします。

### テストの実行

```bash
# すべてのテストを実行
pytest tests/ -v

# カバレッジ測定付きで実行
pytest tests/ --cov=routes --cov=app --cov-report=term-missing

# 特定のテストファイルのみ実行
pytest tests/test_app.py -v
pytest tests/test_routes.py -v
```

**現在のテスト状況（ステップ3完了）:**
- ✅ 80個のテストが実装済み
  - ステップ1: 26テスト（Flaskアプリケーションと基本ルート）
  - ステップ2: 28テスト（タイマーコアロジック）
  - ステップ3: 26テスト（セッション管理とRepository）
- ✅ カバレッジ: 83%
- ✅ TDD（テスト駆動開発）アプローチで実装
- ✅ Clock抽象化による時間制御テスト
- ✅ InMemoryRepositoryによる高速テスト実行

## API 仕様

### タイマー API

- `POST /api/timer/start` - タイマーを開始
- `POST /api/timer/pause` - タイマーを一時停止
- `POST /api/timer/resume` - タイマーを再開
- `POST /api/timer/reset` - タイマーをリセット
- `GET /api/timer/status` - 現在のタイマー状態を取得

### セッション API

- `GET /api/session/today` - 本日の統計を取得
- `POST /api/session/complete` - セッション完了を記録
- `POST /api/session/reset-today` - 本日の統計をリセット

詳細は [architecture.md](architecture.md) を参照してください。

## 開発

### アーキテクチャ

このプロジェクトは、テスト駆動開発とクリーンアーキテクチャの原則に基づいて設計されています。

- **依存性注入**: `Clock` と `Repository` インターフェースにより、テストが容易
- **レイヤー分離**: ルート層、サービス層、モデル層の明確な分離
- **テストダブル**: `MockClock` と `InMemoryRepository` でテストを高速化

詳細な設計については [architecture.md](architecture.md) を参照してください。

### 実装フェーズ

プロジェクトは以下のフェーズに分かれて実装されます：

1. **Phase 1**: バックエンド基本（タイマーロジック）
2. **Phase 2**: フロントエンド基本（UI レイアウト）
3. **Phase 3**: タイマー機能統合（リアルタイム更新）
4. **Phase 4**: 統計・リセット機能
5. **Phase 5**: 設定管理・最適化

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 参考資料

- [features.md](features.md) - 機能仕様書
- [architecture.md](architecture.md) - アーキテクチャ設計書
- [plan.md](plan.md) - 実装計画
