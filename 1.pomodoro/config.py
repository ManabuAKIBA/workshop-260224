"""
ポモドーロタイマー - アプリケーション設定

このモジュールには、アプリケーション全体の設定が含まれています。
"""

import os
from pathlib import Path

# ベースディレクトリ
BASE_DIR = Path(__file__).parent

# Flask 設定
class Config:
    """Flask アプリケーション設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    TESTING = False
    
    # データ保存ディレクトリ
    DATA_DIR = BASE_DIR / 'data'
    SESSION_DATA_FILE = DATA_DIR / 'session_stats.json'
    
    # タイマー設定
    TIMER_WORK_MIN = 5
    TIMER_WORK_MAX = 99
    TIMER_BREAK_MIN = 1
    TIMER_BREAK_MAX = 99
    TIMER_DEFAULT_WORK = 25
    TIMER_DEFAULT_BREAK = 5
    TIMER_LONG_BREAK = 15


class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True


class TestingConfig(Config):
    """テスト環境設定"""
    TESTING = True
    DEBUG = True
    # テスト用のデータディレクトリ
    DATA_DIR = BASE_DIR / 'tests' / 'test_data'
    SESSION_DATA_FILE = DATA_DIR / 'test_session_stats.json'


class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    
    def __init__(self):
        super().__init__()
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")


# 環境変数から設定を選択
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    """環境に応じた設定を取得"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'default')
    return config_map.get(env, DevelopmentConfig)
