"""セッション記録と統計管理"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, Any
from models.timer import TimerState
from models.repository import SessionRepository


@dataclass
class SessionRecord:
    """
    セッション記録のデータクラス
    
    1回のポモドーロセッション（作業/休憩）の情報を保持する
    """
    timestamp: datetime     # セッション完了時刻
    session_type: str       # セッション種類（WORK/BREAK/LONG_BREAK）
    completed: bool         # 完了フラグ
    duration_minutes: int = 0  # セッション時間（分）
    
    def to_dict(self) -> Dict[str, Any]:
        """
        辞書形式に変換（JSON保存用）
        
        Returns:
            セッション情報の辞書
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "session_type": self.session_type,
            "completed": self.completed,
            "duration_minutes": self.duration_minutes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionRecord':
        """
        辞書形式から復元（JSON読込用）
        
        Args:
            data: セッション情報の辞書
            
        Returns:
            SessionRecord インスタンス
        """
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_type=data["session_type"],
            completed=data["completed"],
            duration_minutes=data.get("duration_minutes", 0)
        )


@dataclass
class DailyStats:
    """
    本日の統計データクラス
    
    1日の作業/休憩セッションの集計情報を保持する
    """
    date: date                      # 統計日
    completed_work_sessions: int    # 完了した作業セッション数
    completed_break_sessions: int   # 完了した休憩セッション数
    total_work_minutes: int         # 作業合計時間（分）
    total_break_minutes: int        # 休憩合計時間（分）
    
    def to_dict(self) -> Dict[str, Any]:
        """
        辞書形式に変換
        
        Returns:
            統計情報の辞書
        """
        return {
            "date": self.date.isoformat(),
            "completed_work_sessions": self.completed_work_sessions,
            "completed_break_sessions": self.completed_break_sessions,
            "total_work_minutes": self.total_work_minutes,
            "total_break_minutes": self.total_break_minutes
        }


class SessionManager:
    """
    セッション管理ロジック
    
    セッションの記録と統計計算を担当する
    """
    
    def __init__(self, repository: SessionRepository):
        """
        セッションマネージャーを初期化
        
        Args:
            repository: セッション永続化リポジトリ
        """
        self.repository = repository
    
    def complete_session(self, session_type: str, duration_minutes: int) -> None:
        """
        セッション完了を記録
        
        Args:
            session_type: セッション種類（WORK/BREAK/LONG_BREAK）
            duration_minutes: セッション時間（分）
        """
        record = SessionRecord(
            timestamp=datetime.now(),
            session_type=session_type,
            completed=True,
            duration_minutes=duration_minutes
        )
        self.repository.add_session(record)
    
    def get_today_stats(self) -> DailyStats:
        """
        本日の統計を取得
        
        Returns:
            本日の統計データ
        """
        sessions = self.repository.get_today_sessions()
        
        # 完了したセッションのみ集計
        completed_sessions = [s for s in sessions if s.completed]
        
        # 作業セッション集計
        work_sessions = [
            s for s in completed_sessions 
            if s.session_type == TimerState.WORK
        ]
        
        # 休憩セッション集計（短休憩＋長休憩）
        break_sessions = [
            s for s in completed_sessions 
            if s.session_type in [TimerState.BREAK, TimerState.LONG_BREAK]
        ]
        
        # 実際の時間を合計
        work_minutes = sum(s.duration_minutes for s in work_sessions)
        break_minutes = sum(s.duration_minutes for s in break_sessions)
        
        return DailyStats(
            date=date.today(),
            completed_work_sessions=len(work_sessions),
            completed_break_sessions=len(break_sessions),
            total_work_minutes=work_minutes,
            total_break_minutes=break_minutes
        )
    
    def reset_today(self) -> None:
        """
        本日の統計をリセット
        
        本日のセッション記録を全て削除する
        """
        # 全セッションを取得
        all_sessions = self.repository.get_sessions_by_date_range(
            date.min,  # 最古の日付
            date.max   # 最新の日付
        )
        
        # 本日以外のセッションを保持
        today = date.today()
        other_sessions = [
            s for s in all_sessions
            if s.timestamp.date() != today
        ]
        
        # リポジトリをクリアして、本日以外のセッションを再追加
        self.repository.clear()
        for session in other_sessions:
            self.repository.add_session(session)
