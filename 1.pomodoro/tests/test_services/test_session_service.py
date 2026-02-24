"""
SessionServiceの単体テスト

セッションサービス層のビジネスロジックをテストする
"""

import pytest
from datetime import date
from models.repository import InMemoryRepository
from models.timer import TimerState
from services.session_service import SessionService


class TestSessionServiceInitialization:
    """SessionServiceの初期化テスト"""
    
    def test_service_creation(self):
        """サービスが正常に作成されることを確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        assert service is not None
        assert service.repository == repository
    
    def test_service_has_session_manager(self):
        """サービスがSessionManagerインスタンスを持つことを確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        assert service.session_manager is not None


class TestSessionServiceCompleteSession:
    """SessionService.complete_session()メソッドのテスト"""
    
    def test_complete_work_session_returns_dict(self):
        """complete_session()が辞書を返すことを確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.complete_session(TimerState.WORK, 25)
        
        assert isinstance(result, dict)
    
    def test_complete_work_session_response_structure(self):
        """complete_session()のレスポンス構造を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.complete_session(TimerState.WORK, 25)
        
        assert 'success' in result
        assert 'session_type' in result
        assert 'duration_minutes' in result
    
    def test_complete_work_session_success_flag(self):
        """complete_session()の成功フラグがTrueであることを確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.complete_session(TimerState.WORK, 25)
        
        assert result['success'] is True
    
    def test_complete_work_session_values(self):
        """complete_session()の戻り値を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.complete_session(TimerState.WORK, 25)
        
        assert result['session_type'] == TimerState.WORK
        assert result['duration_minutes'] == 25
    
    def test_complete_break_session(self):
        """休憩セッションの完了記録を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.complete_session(TimerState.BREAK, 5)
        
        assert result['success'] is True
        assert result['session_type'] == TimerState.BREAK
        assert result['duration_minutes'] == 5
    
    def test_complete_long_break_session(self):
        """長休憩セッションの完了記録を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.complete_session(TimerState.LONG_BREAK, 15)
        
        assert result['success'] is True
        assert result['session_type'] == TimerState.LONG_BREAK
        assert result['duration_minutes'] == 15
    
    def test_complete_session_persists_to_repository(self):
        """complete_session()がリポジトリに記録されることを確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        service.complete_session(TimerState.WORK, 25)
        
        sessions = repository.get_today_sessions()
        assert len(sessions) == 1
        assert sessions[0].session_type == TimerState.WORK
        assert sessions[0].duration_minutes == 25
    
    def test_complete_multiple_sessions(self):
        """複数セッションの完了記録を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        service.complete_session(TimerState.WORK, 25)
        service.complete_session(TimerState.BREAK, 5)
        service.complete_session(TimerState.WORK, 25)
        
        sessions = repository.get_today_sessions()
        assert len(sessions) == 3


class TestSessionServiceGetTodayStats:
    """SessionService.get_today_stats()メソッドのテスト"""
    
    def test_get_today_stats_returns_dict(self):
        """get_today_stats()が辞書を返すことを確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.get_today_stats()
        
        assert isinstance(result, dict)
    
    def test_get_today_stats_response_structure(self):
        """get_today_stats()のレスポンス構造を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.get_today_stats()
        
        assert 'date' in result
        assert 'completed_work_sessions' in result
        assert 'completed_break_sessions' in result
        assert 'total_work_minutes' in result
        assert 'total_break_minutes' in result
    
    def test_get_today_stats_empty(self):
        """セッションがない場合のget_today_stats()を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.get_today_stats()
        
        assert result['date'] == date.today().isoformat()
        assert result['completed_work_sessions'] == 0
        assert result['completed_break_sessions'] == 0
        assert result['total_work_minutes'] == 0
        assert result['total_break_minutes'] == 0
    
    def test_get_today_stats_with_work_sessions(self):
        """作業セッションありのget_today_stats()を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        service.complete_session(TimerState.WORK, 25)
        service.complete_session(TimerState.WORK, 25)
        
        result = service.get_today_stats()
        
        assert result['completed_work_sessions'] == 2
        assert result['total_work_minutes'] == 50
        assert result['completed_break_sessions'] == 0
    
    def test_get_today_stats_with_break_sessions(self):
        """休憩セッションありのget_today_stats()を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        service.complete_session(TimerState.BREAK, 5)
        service.complete_session(TimerState.LONG_BREAK, 15)
        
        result = service.get_today_stats()
        
        assert result['completed_work_sessions'] == 0
        assert result['completed_break_sessions'] == 2
        assert result['total_break_minutes'] == 20
    
    def test_get_today_stats_with_mixed_sessions(self):
        """作業と休憩の混合セッションのget_today_stats()を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        service.complete_session(TimerState.WORK, 25)
        service.complete_session(TimerState.BREAK, 5)
        service.complete_session(TimerState.WORK, 25)
        service.complete_session(TimerState.LONG_BREAK, 15)
        
        result = service.get_today_stats()
        
        assert result['completed_work_sessions'] == 2
        assert result['completed_break_sessions'] == 2
        assert result['total_work_minutes'] == 50
        assert result['total_break_minutes'] == 20


class TestSessionServiceResetToday:
    """SessionService.reset_today()メソッドのテスト"""
    
    def test_reset_today_returns_dict(self):
        """reset_today()が辞書を返すことを確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.reset_today()
        
        assert isinstance(result, dict)
    
    def test_reset_today_response_structure(self):
        """reset_today()のレスポンス構造を確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.reset_today()
        
        assert 'success' in result
        assert 'message' in result
    
    def test_reset_today_success_flag(self):
        """reset_today()の成功フラグがTrueであることを確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.reset_today()
        
        assert result['success'] is True
    
    def test_reset_today_clears_sessions(self):
        """reset_today()がセッションをクリアすることを確認"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        # セッションを追加
        service.complete_session(TimerState.WORK, 25)
        service.complete_session(TimerState.BREAK, 5)
        
        # 統計を確認
        stats_before = service.get_today_stats()
        assert stats_before['completed_work_sessions'] == 1
        
        # リセット
        result = service.reset_today()
        assert result['success'] is True
        
        # 統計が0になることを確認
        stats_after = service.get_today_stats()
        assert stats_after['completed_work_sessions'] == 0
        assert stats_after['completed_break_sessions'] == 0
        assert stats_after['total_work_minutes'] == 0


class TestSessionServiceIntegration:
    """SessionServiceの統合テスト"""
    
    def test_complete_and_get_stats_flow(self):
        """セッション完了から統計取得までの一連の流れ"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        # セッションを完了
        complete_result = service.complete_session(TimerState.WORK, 25)
        assert complete_result['success'] is True
        
        # 統計を取得
        stats_result = service.get_today_stats()
        assert stats_result['completed_work_sessions'] == 1
        assert stats_result['total_work_minutes'] == 25
    
    def test_multiple_sessions_and_reset_flow(self):
        """複数セッション記録とリセットの流れ"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        # 複数セッションを完了
        service.complete_session(TimerState.WORK, 25)
        service.complete_session(TimerState.BREAK, 5)
        service.complete_session(TimerState.WORK, 25)
        
        # 統計を確認
        stats1 = service.get_today_stats()
        assert stats1['completed_work_sessions'] == 2
        assert stats1['completed_break_sessions'] == 1
        
        # リセット
        reset_result = service.reset_today()
        assert reset_result['success'] is True
        
        # リセット後の統計を確認
        stats2 = service.get_today_stats()
        assert stats2['completed_work_sessions'] == 0
        assert stats2['completed_break_sessions'] == 0
    
    def test_pomodoro_cycle_simulation(self):
        """ポモドーロサイクルのシミュレーション"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        # 1サイクル目
        service.complete_session(TimerState.WORK, 25)
        service.complete_session(TimerState.BREAK, 5)
        
        # 2サイクル目
        service.complete_session(TimerState.WORK, 25)
        service.complete_session(TimerState.BREAK, 5)
        
        # 3サイクル目
        service.complete_session(TimerState.WORK, 25)
        service.complete_session(TimerState.BREAK, 5)
        
        # 4サイクル目
        service.complete_session(TimerState.WORK, 25)
        service.complete_session(TimerState.LONG_BREAK, 15)
        
        # 統計を確認
        stats = service.get_today_stats()
        assert stats['completed_work_sessions'] == 4
        assert stats['completed_break_sessions'] == 4  # 短休憩3回 + 長休憩1回
        assert stats['total_work_minutes'] == 100  # 25 * 4
        assert stats['total_break_minutes'] == 30  # 5 * 3 + 15


class TestSessionServiceEdgeCases:
    """SessionServiceのエッジケーステスト"""
    
    def test_complete_session_with_zero_duration(self):
        """0分のセッション完了を記録"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.complete_session(TimerState.WORK, 0)
        
        assert result['success'] is True
        assert result['duration_minutes'] == 0
    
    def test_complete_session_with_large_duration(self):
        """大きな時間のセッション完了を記録"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        result = service.complete_session(TimerState.WORK, 99)
        
        assert result['success'] is True
        assert result['duration_minutes'] == 99
    
    def test_reset_empty_today(self):
        """セッションがない状態でのreset_today()"""
        repository = InMemoryRepository()
        service = SessionService(repository)
        
        # セッションがない状態でリセット
        result = service.reset_today()
        
        assert result['success'] is True
        
        # 統計は0のまま
        stats = service.get_today_stats()
        assert stats['completed_work_sessions'] == 0
