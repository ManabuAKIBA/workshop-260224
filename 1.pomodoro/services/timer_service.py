"""
タイマーサービス

タイマーのビジネスロジックを提供するサービス層
"""

from typing import Dict, Any
from models.timer import PomodoroTimer, TimerState
from models.config_model import TimerConfig
from models.clock import Clock


class TimerService:
    """
    タイマーのビジネスロジックを管理するサービス
    
    PomodoroTimerのラッパーとして、APIとモデルの橋渡しをする
    """
    
    def __init__(self, config: TimerConfig, clock: Clock):
        """
        タイマーサービスを初期化
        
        Args:
            config: タイマー設定
            clock: 時刻管理オブジェクト
        """
        self.config = config
        self.clock = clock
        self.timer = PomodoroTimer(config, clock)
    
    def start(self) -> Dict[str, Any]:
        """
        タイマーを開始
        
        Returns:
            Dict[str, Any]: レスポンスデータ
                - success: 成功フラグ
                - state: タイマーの状態
                - remaining: 残り時間（秒）
                - display_time: 表示用時間文字列（MM:SS）
        """
        self.timer.start()
        
        return {
            "success": True,
            "state": self.timer.state,
            "remaining": self.timer.get_remaining(),
            "display_time": self.timer.get_display_time()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        現在のタイマー状態を取得
        
        Returns:
            Dict[str, Any]: タイマー状態データ
                - state: タイマーの状態
                - remaining: 残り時間（秒）
                - display_time: 表示用時間文字列（MM:SS）
                - progress: 進捗率（0.0～1.0）
                - is_paused: 一時停止中フラグ
                - is_completed: 完了フラグ
        """
        return {
            "state": self.timer.state,
            "remaining": self.timer.get_remaining(),
            "display_time": self.timer.get_display_time(),
            "progress": self.timer.get_progress(),
            "is_paused": self.timer.is_paused,
            "is_completed": self.timer.is_completed()
        }
