"""
タイマー設定データモデル

このモジュールには、タイマーの設定を管理するデータクラスが含まれています。
"""

from dataclasses import dataclass


@dataclass
class TimerConfig:
    """
    タイマー設定オブジェクト
    
    ポモドーロタイマーの動作に必要な設定値を保持します。
    """
    
    work_minutes: int = 25
    """作業時間（分）"""
    
    break_minutes: int = 5
    """休憩時間（分）"""
    
    long_break_minutes: int = 15
    """長休憩時間（分）- 4セッション後"""
    
    min_minutes: int = 5
    """最小時間（分）"""
    
    max_minutes: int = 99
    """最大時間（分）"""
    
    def validate(self) -> bool:
        """
        設定値のバリデーション
        
        Returns:
            bool: 設定値が有効な場合True
        """
        return (
            self.min_minutes <= self.work_minutes <= self.max_minutes and
            self.min_minutes <= self.break_minutes <= self.max_minutes and
            self.min_minutes <= self.long_break_minutes <= self.max_minutes
        )
    
    def reset(self) -> None:
        """デフォルト設定にリセット"""
        self.work_minutes = 25
        self.break_minutes = 5
        self.long_break_minutes = 15
    
    def work_duration_seconds(self) -> int:
        """
        作業時間を秒単位で取得
        
        Returns:
            int: 作業時間（秒）
        """
        return self.work_minutes * 60
    
    def break_duration_seconds(self) -> int:
        """
        休憩時間を秒単位で取得
        
        Returns:
            int: 休憩時間（秒）
        """
        return self.break_minutes * 60
    
    def long_break_duration_seconds(self) -> int:
        """
        長休憩時間を秒単位で取得
        
        Returns:
            int: 長休憩時間（秒）
        """
        return self.long_break_minutes * 60
