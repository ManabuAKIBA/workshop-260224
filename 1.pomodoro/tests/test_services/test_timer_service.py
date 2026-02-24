"""
TimerServiceの単体テスト

タイマーサービス層のビジネスロジックをテストする
"""

import pytest
from models.clock import MockClock
from models.config_model import TimerConfig
from services.timer_service import TimerService


class TestTimerServiceInitialization:
    """TimerServiceの初期化テスト"""
    
    def test_service_creation(self):
        """サービスが正常に作成されることを確認"""
        config = TimerConfig(work_minutes=25, break_minutes=5)
        clock = MockClock()
        service = TimerService(config, clock)
        
        assert service is not None
        assert service.config == config
        assert service.clock == clock
    
    def test_service_has_timer(self):
        """サービスがPomodoroTimerインスタンスを持つことを確認"""
        config = TimerConfig(work_minutes=25, break_minutes=5)
        clock = MockClock()
        service = TimerService(config, clock)
        
        assert service.timer is not None
    
    def test_service_with_custom_config(self):
        """カスタム設定でサービスを作成できることを確認"""
        config = TimerConfig(work_minutes=50, break_minutes=10)
        clock = MockClock()
        service = TimerService(config, clock)
        
        assert service.config.work_minutes == 50
        assert service.config.break_minutes == 10


class TestTimerServiceStart:
    """TimerService.start()メソッドのテスト"""
    
    def test_start_returns_dict(self):
        """start()が辞書を返すことを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.start()
        
        assert isinstance(result, dict)
    
    def test_start_response_structure(self):
        """start()のレスポンス構造を確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.start()
        
        assert 'success' in result
        assert 'state' in result
        assert 'remaining' in result
        assert 'display_time' in result
    
    def test_start_success_flag(self):
        """start()の成功フラグがTrueであることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.start()
        
        assert result['success'] is True
    
    def test_start_sets_work_state(self):
        """start()で作業状態が設定されることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.start()
        
        assert result['state'] == 'work'
    
    def test_start_sets_remaining_time(self):
        """start()で残り時間が設定されることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.start()
        
        expected_seconds = 25 * 60
        assert result['remaining'] == expected_seconds
    
    def test_start_display_time_format(self):
        """start()の表示時間がMM:SS形式であることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.start()
        
        assert result['display_time'] == '25:00'
    
    def test_start_with_different_duration(self):
        """異なる作業時間でstart()を実行"""
        config = TimerConfig(work_minutes=10)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.start()
        
        assert result['remaining'] == 10 * 60
        assert result['display_time'] == '10:00'


class TestTimerServiceGetStatus:
    """TimerService.get_status()メソッドのテスト"""
    
    def test_get_status_returns_dict(self):
        """get_status()が辞書を返すことを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.get_status()
        
        assert isinstance(result, dict)
    
    def test_get_status_response_structure(self):
        """get_status()のレスポンス構造を確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.get_status()
        
        assert 'state' in result
        assert 'remaining' in result
        assert 'display_time' in result
        assert 'progress' in result
        assert 'is_paused' in result
        assert 'is_completed' in result
    
    def test_get_status_before_start(self):
        """開始前のget_status()の状態を確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.get_status()
        
        assert result['state'] == 'stopped'
        assert result['is_paused'] is False
        assert result['is_completed'] is False
    
    def test_get_status_after_start(self):
        """開始後のget_status()の状態を確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        service = TimerService(config, clock)
        
        service.start()
        result = service.get_status()
        
        assert result['state'] == 'work'
        assert result['remaining'] == 25 * 60
        assert result['is_paused'] is False
    
    def test_get_status_progress_range(self):
        """get_status()の進捗率が0.0～1.0の範囲であることを確認"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock()
        service = TimerService(config, clock)
        
        result = service.get_status()
        
        assert 0.0 <= result['progress'] <= 1.0
    
    def test_get_status_during_countdown(self):
        """カウントダウン中のget_status()を確認"""
        config = TimerConfig(work_minutes=10)
        clock = MockClock(initial_time=0.0)
        service = TimerService(config, clock)
        
        service.start()
        clock.advance(5 * 60)  # 5分経過
        
        result = service.get_status()
        
        assert result['state'] == 'work'
        assert result['remaining'] == 5 * 60
        assert result['display_time'] == '05:00'
        assert result['progress'] == pytest.approx(0.5)
    
    def test_get_status_at_completion(self):
        """完了時のget_status()を確認"""
        config = TimerConfig(work_minutes=5)
        clock = MockClock(initial_time=0.0)
        service = TimerService(config, clock)
        
        service.start()
        clock.advance(5 * 60)  # 5分経過（完了）
        
        result = service.get_status()
        
        assert result['remaining'] == 0
        assert result['is_completed'] is True
        assert result['progress'] == pytest.approx(1.0)


class TestTimerServiceIntegration:
    """TimerServiceの統合テスト"""
    
    def test_start_and_get_status_flow(self):
        """start()してからget_status()する一連の流れ"""
        config = TimerConfig(work_minutes=25)
        clock = MockClock(initial_time=0.0)
        service = TimerService(config, clock)
        
        # タイマーを開始
        start_result = service.start()
        assert start_result['success'] is True
        assert start_result['state'] == 'work'
        
        # 状態を確認
        status_result = service.get_status()
        assert status_result['state'] == 'work'
        assert status_result['remaining'] <= 25 * 60
    
    def test_multiple_starts_reset_timer(self):
        """複数回start()すると、タイマーがリセットされることを確認"""
        config = TimerConfig(work_minutes=10)
        clock = MockClock(initial_time=0.0)
        service = TimerService(config, clock)
        
        # 1回目の開始
        service.start()
        clock.advance(5 * 60)  # 5分経過
        
        status1 = service.get_status()
        assert status1['remaining'] == 5 * 60
        
        # 2回目の開始
        service.start()
        status2 = service.get_status()
        
        # リセットされて10分に戻る
        assert status2['remaining'] == 10 * 60
    
    def test_timer_with_mock_clock(self):
        """MockClockを使ったタイマーの動作確認"""
        config = TimerConfig(work_minutes=15)
        clock = MockClock(initial_time=0.0)
        service = TimerService(config, clock)
        
        service.start()
        
        # 3分経過
        clock.advance(3 * 60)
        status1 = service.get_status()
        assert status1['remaining'] == 12 * 60
        assert status1['display_time'] == '12:00'
        
        # さらに7分経過（合計10分）
        clock.advance(7 * 60)
        status2 = service.get_status()
        assert status2['remaining'] == 5 * 60
        assert status2['display_time'] == '05:00'
        assert status2['progress'] == pytest.approx(10/15)


class TestTimerServiceEdgeCases:
    """TimerServiceのエッジケーステスト"""
    
    def test_service_with_minimum_duration(self):
        """最小作業時間でのサービステスト"""
        config = TimerConfig(work_minutes=1, break_minutes=1, min_minutes=1, max_minutes=99)
        clock = MockClock(initial_time=0.0)
        service = TimerService(config, clock)
        
        result = service.start()
        
        assert result['remaining'] == 60
        assert result['display_time'] == '01:00'
    
    def test_service_with_maximum_duration(self):
        """最大作業時間でのサービステスト"""
        config = TimerConfig(work_minutes=99, break_minutes=5, min_minutes=1, max_minutes=99)
        clock = MockClock(initial_time=0.0)
        service = TimerService(config, clock)
        
        result = service.start()
        
        assert result['remaining'] == 99 * 60
        assert result['display_time'] == '99:00'
    
    def test_get_status_when_time_exceeds(self):
        """時間超過時のget_status()を確認"""
        config = TimerConfig(work_minutes=5)
        clock = MockClock(initial_time=0.0)
        service = TimerService(config, clock)
        
        service.start()
        clock.advance(10 * 60)  # 作業時間の倍経過
        
        result = service.get_status()
        
        # 残り時間は0以下にならない
        assert result['remaining'] == 0
        assert result['is_completed'] is True
        # 進捗率は1.0を超えない
        assert result['progress'] <= 1.0
