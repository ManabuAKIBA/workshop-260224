"""
ポモドーロタイマー - Webページ描画

このモジュールには、HTMLページを描画するルートが含まれています。
"""

from flask import Blueprint, render_template

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    """
    メインページを表示
    
    Returns:
        str: レンダリングされたHTML
    """
    return render_template('index.html')


@web_bp.route('/health')
def health():
    """
    ヘルスチェックエンドポイント
    
    Returns:
        dict: ステータス情報
    """
    return {'status': 'ok', 'message': 'Application is running'}
