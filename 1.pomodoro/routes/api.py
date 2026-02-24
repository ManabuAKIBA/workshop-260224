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


@api_bp.route('/timer/pause', methods=['POST'])
def pause_timer():
    """
    タイマー一時停止エンドポイント
    
    POST /api/timer/pause
    
    Returns:
        JSONレスポンス: タイマー状態
    """
    timer_service = current_app.timer_service
    status = timer_service.pause()
    return jsonify(status)


@api_bp.route('/timer/resume', methods=['POST'])
def resume_timer():
    """
    タイマー再開エンドポイント
    
    POST /api/timer/resume
    
    Returns:
        JSONレスポンス: タイマー状態
    """
    timer_service = current_app.timer_service
    status = timer_service.resume()
    return jsonify(status)


@api_bp.route('/timer/reset', methods=['POST'])
def reset_timer():
    """
    タイマーリセットエンドポイント
    
    POST /api/timer/reset
    
    Returns:
        JSONレスポンス: タイマー状態
    """
    timer_service = current_app.timer_service
    status = timer_service.reset()
    return jsonify(status)

