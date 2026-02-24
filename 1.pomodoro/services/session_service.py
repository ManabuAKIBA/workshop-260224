"""
セッションサービス

セッション管理のビジネスロジックを提供するサービス層
"""

from typing import Dict, Any
from models.session import SessionManager
from models.clock import Clock


class SessionService:
    """
    セッション管理のビジネスロジックを管理するサービス
    
    SessionManagerのラッパーとして、APIとモデルの橋渡しをする
    """
    
    def __init__(self, session_manager: SessionManager, clock: Clock):
        """
        セッションサービスを初期化
        
        Args:
            session_manager: セッション管理オブジェクト
            clock: 時刻管理オブジェクト
        """
        self.session_manager = session_manager
        self.clock = clock
    
    def complete_session(self, session_type: str, duration_minutes: int) -> Dict[str, Any]:
        """
        セッションを完了として記録
        
        Args:
            session_type: セッション種類（WORK/BREAK/LONG_BREAK）
            duration_minutes: セッション時間（分）
        
        Returns:
            Dict[str, Any]: レスポンスデータ
                - success: 成功フラグ
                - message: メッセージ
        """
        self.session_manager.complete_session(session_type, duration_minutes)
        
        return {
            "success": True,
            "message": f"Session completed: {session_type} for {duration_minutes} minutes"
        }
    
    def get_today_stats(self) -> Dict[str, Any]:
        """
        本日の統計を取得
        
        Returns:
            Dict[str, Any]: 統計データ
                - date: 統計日
                - completed_work_sessions: 完了した作業セッション数
                - completed_break_sessions: 完了した休憩セッション数
                - total_work_minutes: 作業合計時間（分）
                - total_break_minutes: 休憩合計時間（分）
        """
        stats = self.session_manager.get_today_stats()
        return stats.to_dict()
