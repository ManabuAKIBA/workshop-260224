"""
タイマーロジックのテスト

TDD（テスト駆動開発）アプローチで実装します。
"""

import pytest
from models.clock import MockClock
from models.config_model import TimerConfig
from models.timer import PomodoroTimer, TimerState


class TestTimerState:
    """TimerStateの定数テスト"""
    
    def test_timer_states_exist(self):
        """タイマー状態の定数が存在することを確認"""
        assert hasattr(TimerState, 'WORK')
        assert hasattr(TimerState, 'BREAK')
        assert hasattr(TimerState, 'LONG_BREAK')
        assert hasattr(TimerState, 'STOPPED')
    
    def test_timer_state_values(self):
        """タイマー状態の値を確認"""
        assert TimerState.WORK == "work"
        assert TimerState.BREAK == "break"
        assert TimerState.LONG_BREAK == "long_break"
        assert TimerState.STOPPED == "stopped"


class TestPomodoroTimerInitialization:
    """PomodoroTimerの初期化テスト"""
    
    def test_timer_creation(self):
        """タイマーが正常に作成されることを確認"""
        config = TimerConfig(work_minutes=25, break_minutes=5)
        clock = MockClock()
        timer = PomodoroTimer(config, clock)
        
        assert timer is not None
        assert timer.config == config
        assert timer.clock == clock
    
    def test_initial_state_is_stopped(self):
        """初期状態がSTOPPEDであることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        timer = PomodoroTimer(config, clock)
        
        assert timer.state == TimerState.STOPPED
        assert timer.is_paused is False
    
    def test_initial_remaining_time(self):
        """初期の残り時間が作業時間と一致することを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        timer = PomodoroTimer(config, clock)
        
        expected_seconds = 25 * 60
        assert timer.get_remaining() == expected_seconds


class TestTimerStart:
    """タイマー開始のテスト"""
    
    def test_start_timer(self):
        """タイマーを開始できることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        
        assert timer.state == TimerState.WORK
        assert timer.is_paused is False
        assert timer.start_time == 0.0
    
    def test_remaining_time_after_start(self):
        """開始直後の残り時間を確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=100.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        
        expected = 25 * 60
        assert timer.get_remaining() == expected


class TestTimerCountdown:
    """タイマーのカウントダウンテスト"""
    
    def test_countdown_with_mock_clock(self):
        """MockClockで時間を進めたときの残り時間を確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        
        # 5分経過
        clock.advance(5 * 60)
        remaining = timer.get_remaining()
        
        expected = (25 - 5) * 60  # 20分
        assert remaining == expected
    
    def test_countdown_multiple_advances(self):
        """複数回時間を進めたときの動作を確認"""
        config = TimerConfig(work_minutes=10)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        
        # 3分経過
        clock.advance(3 * 60)
        assert timer.get_remaining() == 7 * 60
        
        # さらに4分経過（合計7分）
        clock.advance(4 * 60)
        assert timer.get_remaining() == 3 * 60
    
    def test_remaining_does_not_go_negative(self):
        """残り時間が負にならないことを確認"""
        config = TimerConfig(work_minutes=5)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        
        # 10分経過（作業時間の5分を超える）
        clock.advance(10 * 60)
        
        assert timer.get_remaining() == 0
        assert timer.get_remaining() >= 0


class TestTimerProgress:
    """進捗率のテスト"""
    
    def test_progress_at_start(self):
        """開始直後の進捗率は0.0"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        
        assert timer.get_progress() == 0.0
    
    def test_progress_halfway(self):
        """中間地点の進捗率は0.5"""
        config = TimerConfig(work_minutes=10)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(5 * 60)  # 5分経過（半分）
        
        assert timer.get_progress() == pytest.approx(0.5)
    
    def test_progress_at_completion(self):
        """完了時の進捗率は1.0"""
        config = TimerConfig(work_minutes=5)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(5 * 60)  # 5分経過（完了）
        
        assert timer.get_progress() == pytest.approx(1.0)
    
    def test_progress_does_not_exceed_one(self):
        """進捗率が1.0を超えないことを確認"""
        config = TimerConfig(work_minutes=5)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(10 * 60)  # 10分経過（超過）
        
        assert timer.get_progress() <= 1.0


class TestTimerCompletion:
    """タイマー完了判定のテスト"""
    
    def test_not_completed_at_start(self):
        """開始直後は完了していない"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        
        assert timer.is_completed() is False
    
    def test_not_completed_during_countdown(self):
        """カウントダウン中は完了していない"""
        config = TimerConfig(work_minutes=10)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(5 * 60)  # 5分経過
        
        assert timer.is_completed() is False
    
    def test_completed_when_time_is_up(self):
        """時間が経過したら完了"""
        config = TimerConfig(work_minutes=5)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(5 * 60)  # 5分経過（完了）
        
        assert timer.is_completed() is True


class TestTimerPauseResume:
    """一時停止と再開のテスト"""
    
    def test_pause_timer(self):
        """タイマーを一時停止できることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(5 * 60)  # 5分経過
        timer.pause()
        
        assert timer.is_paused is True
        assert timer.get_remaining() == 20 * 60
    
    def test_time_stops_when_paused(self):
        """一時停止中は時間が進まないことを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(5 * 60)  # 5分経過
        timer.pause()
        
        remaining_when_paused = timer.get_remaining()
        
        # 一時停止中に時間が進む
        clock.advance(10 * 60)
        
        # 残り時間は変わらない
        assert timer.get_remaining() == remaining_when_paused
    
    def test_resume_timer(self):
        """一時停止したタイマーを再開できることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(5 * 60)  # 5分経過
        timer.pause()
        clock.advance(10 * 60)  # 一時停止中に10分経過
        timer.resume()
        
        assert timer.is_paused is False
        assert timer.get_remaining() == 20 * 60
    
    def test_time_continues_after_resume(self):
        """再開後は時間が進むことを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(5 * 60)  # 5分経過
        timer.pause()
        clock.advance(10 * 60)  # 一時停止中
        timer.resume()
        
        # 再開後さらに3分経過
        clock.advance(3 * 60)
        
        assert timer.get_remaining() == 17 * 60


class TestTimerReset:
    """リセット機能のテスト"""
    
    def test_reset_timer(self):
        """タイマーをリセットできることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(10 * 60)  # 10分経過
        timer.reset()
        
        assert timer.state == TimerState.STOPPED
        assert timer.is_paused is False
        assert timer.get_remaining() == 25 * 60
    
    def test_reset_from_paused_state(self):
        """一時停止状態からリセットできることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(5 * 60)
        timer.pause()
        timer.reset()
        
        assert timer.state == TimerState.STOPPED
        assert timer.is_paused is False


class TestTimerDisplayTime:
    """表示用時間文字列のテスト"""
    
    def test_display_time_format(self):
        """MM:SS形式で表示されることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        display_time = timer.get_display_time()
        
        assert display_time == "25:00"
    
    def test_display_time_after_countdown(self):
        """カウントダウン後の表示時間を確認"""
        config = TimerConfig(work_minutes=10)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(3 * 60 + 30)  # 3分30秒経過
        
        assert timer.get_display_time() == "06:30"
    
    def test_display_time_with_single_digits(self):
        """1桁の数値が0埋めされることを確認"""
        config = TimerConfig(work_minutes=5)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        clock.advance(4 * 60 + 55)  # 4分55秒経過（残り5秒）
        
        assert timer.get_display_time() == "00:05"


class TestTimerWithDifferentConfigurations:
    """異なる設定でのタイマーテスト"""
    
    def test_short_timer(self):
        """短い作業時間のテスト"""
        config = TimerConfig(work_minutes=5)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        
        assert timer.get_remaining() == 5 * 60
    
    def test_long_timer(self):
        """長い作業時間のテスト"""
        config = TimerConfig(work_minutes=99)
        clock = MockClock(initial_time=0.0)
        timer = PomodoroTimer(config, clock)
        
        timer.start()
        
        assert timer.get_remaining() == 99 * 60
        assert timer.get_display_time() == "99:00"
