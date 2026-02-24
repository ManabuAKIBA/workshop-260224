"""
タイマーAPI ルート

タイマー操作のためのREST APIエンドポイント
"""

from flask import Blueprint, jsonify, current_app, request


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


@api_bp.route('/session/today', methods=['GET'])
def get_today_stats():
    """
    本日の統計取得エンドポイント
    
    GET /api/session/today
    
    Returns:
        JSONレスポンス:
            - date: 統計日
            - completed_work_sessions: 完了した作業セッション数
            - completed_break_sessions: 完了した休憩セッション数
            - total_work_minutes: 作業合計時間（分）
            - total_break_minutes: 休憩合計時間（分）
    """
    session_service = current_app.session_service
    stats = session_service.get_today_stats()
    return jsonify(stats)


@api_bp.route('/session/complete', methods=['POST'])
def complete_session():
    """
    セッション完了記録エンドポイント
    
    POST /api/session/complete
    
    Request Body:
        {
            "session_type": "work" | "break" | "long_break",
            "duration_minutes": 25
        }
    
    Returns:
        JSONレスポンス:
            - success: 成功フラグ
            - message: メッセージ
    """
    session_service = current_app.session_service
    data = request.get_json()
    
    # リクエストボディの検証
    if not data or 'session_type' not in data or 'duration_minutes' not in data:
        return jsonify({
            "success": False,
            "message": "Invalid request: session_type and duration_minutes are required"
        }), 400
    
    session_type = data['session_type']
    duration_minutes = data['duration_minutes']
    
    result = session_service.complete_session(session_type, duration_minutes)
    return jsonify(result)
