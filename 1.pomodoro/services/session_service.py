"""
セッションサービス

セッション管理のビジネスロジックを提供するサービス層
"""

from typing import Dict, Any
from models.session import SessionManager, DailyStats
from models.repository import SessionRepository


class SessionService:
    """
    セッション管理のビジネスロジックを管理するサービス
    
    SessionManagerのラッパーとして、APIとモデルの橋渡しをする
    """
    
    def __init__(self, repository: SessionRepository):
        """
        セッションサービスを初期化
        
        Args:
            repository: セッション永続化リポジトリ
        """
        self.repository = repository
        self.session_manager = SessionManager(repository)
    
    def complete_session(self, session_type: str, duration_minutes: int) -> Dict[str, Any]:
        """
        セッション完了を記録
        
        Args:
            session_type: セッション種類（WORK/BREAK/LONG_BREAK）
            duration_minutes: セッション時間（分）
        
        Returns:
            Dict[str, Any]: レスポンスデータ
                - success: 成功フラグ
                - session_type: 記録されたセッション種類
                - duration_minutes: 記録された時間
        """
        self.session_manager.complete_session(session_type, duration_minutes)
        
        return {
            "success": True,
            "session_type": session_type,
            "duration_minutes": duration_minutes
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
    
    def reset_today(self) -> Dict[str, Any]:
        """
        本日の統計をリセット
        
        Returns:
            Dict[str, Any]: レスポンスデータ
                - success: 成功フラグ
                - message: メッセージ
        """
        self.session_manager.reset_today()
        
        return {
            "success": True,
            "message": "Today's statistics have been reset"
        }
