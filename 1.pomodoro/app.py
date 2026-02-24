"""
ポモドーロタイマー Web アプリケーション

Flask アプリケーションのエントリーポイント
"""

from flask import Flask
from pathlib import Path

from config import get_config
from routes.web import web_bp
from routes.api import api_bp
from models.clock import RealClock, MockClock
from models.config_model import TimerConfig
from services.timer_service import TimerService


def create_app(config_name=None, clock=None):
    """
    Flask アプリケーションファクトリー
    
    Args:
        config_name: 設定名 ('development', 'testing', 'production')
        clock: 時刻管理オブジェクト（テスト用にMockClockを注入可能）
    
    Returns:
        Flask: 設定済みの Flask アプリケーション
    """
    app = Flask(__name__)
    
    # 設定を読み込み
    config = get_config(config_name)
    app.config.from_object(config)
    
    # データディレクトリを作成
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 依存性の初期化
    # テスト環境ではMockClockを注入可能にする
    if clock is None:
        if app.config['TESTING']:
            clock = MockClock()
        else:
            clock = RealClock()
    
    timer_config = TimerConfig(
        work_minutes=config.TIMER_DEFAULT_WORK,
        break_minutes=config.TIMER_DEFAULT_BREAK,
        long_break_minutes=config.TIMER_LONG_BREAK
    )
    
    # サービスの初期化
    timer_service = TimerService(timer_config, clock)
    
    # アプリケーションにサービスとクロックを注入
    app.timer_service = timer_service
    app.clock = clock  # テスト時にクロックを操作できるようにする
    
    # Blueprintの登録
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
