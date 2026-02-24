"""
ポモドーロタイマー Web アプリケーション

Flask アプリケーションのエントリーポイント
"""

from flask import Flask
from pathlib import Path

from config import get_config
from routes.web import web_bp


def create_app(config_name=None):
    """
    Flask アプリケーションファクトリー
    
    Args:
        config_name: 設定名 ('development', 'testing', 'production')
    
    Returns:
        Flask: 設定済みの Flask アプリケーション
    """
    app = Flask(__name__)
    
    # 設定を読み込み
    config = get_config(config_name)
    app.config.from_object(config)
    
    # データディレクトリを作成
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Blueprintの登録
    app.register_blueprint(web_bp)
    
    # 依存性の初期化は Phase 2 以降で実装予定
    # - Clock の初期化
    # - Repository の初期化
    # - Timer, SessionManager の初期化
    # - Service 層の初期化
    # - API Routes の登録
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
