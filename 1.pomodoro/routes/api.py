"""
タイマーAPI ルート

タイマー操作のためのREST APIエンドポイント
"""

from flask import Blueprint, jsonify, current_app


api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/timer/start', methods=['POST'])
def start_timer():
    """
    タイマー開始エンドポイント
    
    POST /api/timer/start
    
    Returns:
        JSONレスポンス:
            - success: 成功フラグ
            - state: タイマーの状態
            - remaining: 残り時間（秒）
            - display_time: 表示用時間文字列（MM:SS）
    """
    timer_service = current_app.timer_service
    result = timer_service.start()
    return jsonify(result)


@api_bp.route('/timer/status', methods=['GET'])
def get_timer_status():
    """
    タイマー状態取得エンドポイント
    
    GET /api/timer/status
    
    Returns:
        JSONレスポンス:
            - state: タイマーの状態
            - remaining: 残り時間（秒）
            - display_time: 表示用時間文字列（MM:SS）
            - progress: 進捗率（0.0～1.0）
            - is_paused: 一時停止中フラグ
            - is_completed: 完了フラグ
    """
    timer_service = current_app.timer_service
    status = timer_service.get_status()
    return jsonify(status)
