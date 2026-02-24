"""
pytest 設定ファイル

共通のフィクスチャとテスト設定を定義します。
"""

import sys
from pathlib import Path

import pytest

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app


@pytest.fixture
def app():
    """テスト用のFlaskアプリケーション"""
    app = create_app('testing')
    
    # テスト実行前にリポジトリをクリア
    if hasattr(app, 'session_service'):
        app.session_service.session_manager.repository.clear()
    
    yield app
    
    # テスト実行後もクリア
    if hasattr(app, 'session_service'):
        app.session_service.session_manager.repository.clear()


@pytest.fixture
def client(app):
    """テスト用のFlaskクライアント"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """テスト用のCLIランナー"""
    return app.test_cli_runner()


# ステップ2で追加: タイマー関連のフィクスチャ
@pytest.fixture
def mock_clock():
    """テスト用のモッククロック"""
    from models.clock import MockClock
    return MockClock(initial_time=0.0)


@pytest.fixture
def timer_config():
    """テスト用のタイマー設定"""
    from models.config_model import TimerConfig
    return TimerConfig(
        work_minutes=25,
        break_minutes=5,
        min_minutes=5,
        max_minutes=99
    )


@pytest.fixture
def short_timer_config():
    """テスト用の短いタイマー設定（テストを高速化）"""
    from models.config_model import TimerConfig
    return TimerConfig(
        work_minutes=1,  # 1分
        break_minutes=1,
        min_minutes=1,
        max_minutes=99
    )


# 以下のフィクスチャはステップ3以降で使用
# @pytest.fixture
# def in_memory_repository():
#     """テスト用のインメモリリポジトリ"""
#     from models.repository import InMemoryRepository
#     return InMemoryRepository()
