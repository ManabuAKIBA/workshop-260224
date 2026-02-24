"""
ポモドーロタイマーのコアロジック

このモジュールには、タイマーの状態管理とカウントダウンロジックが含まれています。
"""

from typing import Optional
from models.clock import Clock
from models.config_model import TimerConfig


class TimerState:
    """タイマーの状態定義"""
    WORK = "work"
    BREAK = "break"
    LONG_BREAK = "long_break"
    STOPPED = "stopped"


class PomodoroTimer:
    """
    ポモドーロタイマーの核となるロジック
    
    Clock インターフェースに依存することで、
    テスト時にシステム時刻を制御可能にする。
    """
    
    def __init__(self, config: TimerConfig, clock: Clock):
        """
        タイマーを初期化
        
        Args:
            config: タイマー設定
            clock: 時刻管理オブジェクト
        """
        self.config = config
        self.clock = clock
        
        self.start_time: Optional[float] = None
        self.paused_elapsed: int = 0
        self.state: str = TimerState.STOPPED
        self.is_paused: bool = False
    
    def start(self) -> None:
        """タイマーを開始"""
        self.start_time = self.clock.now()
        self.state = TimerState.WORK
        self.is_paused = False
        self.paused_elapsed = 0
    
    def pause(self) -> None:
        """タイマーを一時停止"""
        if not self.is_paused and self.start_time is not None:
            self.paused_elapsed = self.get_elapsed()
            self.is_paused = True
    
    def resume(self) -> None:
        """タイマーを再開"""
        if self.is_paused:
            self.start_time = self.clock.now() - self.paused_elapsed
            self.is_paused = False
    
    def reset(self) -> None:
        """タイマーをリセット"""
        self.start_time = None
        self.paused_elapsed = 0
        self.state = TimerState.STOPPED
        self.is_paused = False
    
    def get_elapsed(self) -> int:
        """
        経過秒数を取得
        
        Returns:
            int: 経過秒数
        """
        if self.start_time is None:
            return 0
        
        if self.is_paused:
            return self.paused_elapsed
        
        return int(self.clock.now() - self.start_time)
    
    def get_remaining(self) -> int:
        """
        残り秒数を取得
        
        Returns:
            int: 残り秒数（0以上）
        """
        duration = self._get_current_duration()
        elapsed = self.get_elapsed()
        remaining = duration - elapsed
        return max(0, remaining)
    
    def get_progress(self) -> float:
        """
        進捗率を取得（0.0～1.0）
        
        Returns:
            float: 進捗率
        """
        duration = self._get_current_duration()
        if duration == 0:
            return 0.0
        
        elapsed = self.get_elapsed()
        progress = elapsed / duration
        return min(1.0, progress)
    
    def is_completed(self) -> bool:
        """
        セッションが完了したか判定
        
        Returns:
            bool: 完了している場合True
        """
        return self.get_remaining() == 0 and self.start_time is not None
    
    def get_display_time(self) -> str:
        """
        表示用時間文字列を取得（MM:SS形式）
        
        Returns:
            str: MM:SS形式の時間文字列
        """
        remaining = self.get_remaining()
        mins = remaining // 60
        secs = remaining % 60
        return f"{mins:02d}:{secs:02d}"
    
    def _get_current_duration(self) -> int:
        """
        現在の状態に応じた持続時間を取得
        
        Returns:
            int: 持続時間（秒）
        """
        if self.state == TimerState.WORK:
            return self.config.work_duration_seconds()
        elif self.state == TimerState.BREAK:
            return self.config.break_duration_seconds()
        elif self.state == TimerState.LONG_BREAK:
            return self.config.long_break_duration_seconds()
        else:
            return self.config.work_duration_seconds()
