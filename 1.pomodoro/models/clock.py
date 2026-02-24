"""
時間管理の抽象化

このモジュールには、時間アクセスを抽象化するインターフェースと実装が含まれています。
テスト時にシステム時刻を制御可能にすることで、テストの信頼性と再現性を向上させます。
"""

from abc import ABC, abstractmethod
import time


class Clock(ABC):
    """
    時間アクセスの抽象インターフェース
    
    このインターフェースにより、本番環境とテスト環境で異なる時刻実装を使用できます。
    """
    
    @abstractmethod
    def now(self) -> float:
        """
        現在のUNIXタイムスタンプを返す
        
        Returns:
            float: 現在時刻のUNIXタイムスタンプ（秒単位）
        """
        pass


class RealClock(Clock):
    """
    本番用：実際のシステム時刻を返す実装
    
    本番環境では、実際のシステム時刻を使用してタイマーを動作させます。
    """
    
    def now(self) -> float:
        """
        実際のシステム時刻を返す
        
        Returns:
            float: 現在のシステム時刻（UNIXタイムスタンプ）
        """
        return time.time()


class MockClock(Clock):
    """
    テスト用：時刻を制御可能な実装
    
    テスト時には、時刻を手動で制御することで、
    タイマーの動作を確実にテストできます。
    """
    
    def __init__(self, initial_time: float = 0.0):
        """
        モッククロックを初期化
        
        Args:
            initial_time: 初期時刻（デフォルト: 0.0）
        """
        self._current_time = initial_time
    
    def now(self) -> float:
        """
        設定された時刻を返す
        
        Returns:
            float: 現在設定されている時刻
        """
        return self._current_time
    
    def advance(self, seconds: float) -> None:
        """
        時刻を進める（テスト用）
        
        Args:
            seconds: 進める秒数
        """
        self._current_time += seconds
    
    def set_time(self, timestamp: float) -> None:
        """
        時刻を特定の値に設定する（テスト用）
        
        Args:
            timestamp: 設定する時刻
        """
        self._current_time = timestamp
