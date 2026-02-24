"""セッション管理機能のテスト"""
import pytest
from datetime import datetime, timedelta, date
from models.session import SessionRecord, DailyStats, SessionManager
from models.repository import InMemoryRepository
from models.timer import TimerState


class TestSessionRecord:
    """SessionRecord データクラスのテスト"""

    def test_session_record_creation(self):
        """セッションレコードの作成テスト"""
        now = datetime.now()
        record = SessionRecord(
            timestamp=now,
            session_type=TimerState.WORK,
            completed=True,
            duration_minutes=25
        )
        assert record.timestamp == now
        assert record.session_type == TimerState.WORK
        assert record.completed is True
        assert record.duration_minutes == 25

    def test_session_record_work_type(self):
        """作業セッションの記録テスト"""
        record = SessionRecord(
            timestamp=datetime.now(),
            session_type=TimerState.WORK,
            completed=True,
            duration_minutes=25
        )
        assert record.session_type == TimerState.WORK

    def test_session_record_break_type(self):
        """休憩セッションの記録テスト"""
        record = SessionRecord(
            timestamp=datetime.now(),
            session_type=TimerState.BREAK,
            completed=True,
            duration_minutes=5
        )
        assert record.session_type == TimerState.BREAK

    def test_session_record_long_break_type(self):
        """長休憩セッションの記録テスト"""
        record = SessionRecord(
            timestamp=datetime.now(),
            session_type=TimerState.LONG_BREAK,
            completed=True,
            duration_minutes=15
        )
        assert record.session_type == TimerState.LONG_BREAK

    def test_session_record_incomplete(self):
        """未完了セッションの記録テスト"""
        record = SessionRecord(
            timestamp=datetime.now(),
            session_type=TimerState.WORK,
            completed=False,
            duration_minutes=0
        )
        assert record.completed is False

    def test_session_record_to_dict(self):
        """セッションレコード→辞書変換テスト"""
        now = datetime.now()
        record = SessionRecord(
            timestamp=now,
            session_type=TimerState.WORK,
            completed=True,
            duration_minutes=25
        )
        data = record.to_dict()
        assert data["timestamp"] == now.isoformat()
        assert data["session_type"] == TimerState.WORK
        assert data["completed"] is True
        assert data["duration_minutes"] == 25

    def test_session_record_from_dict(self):
        """辞書→セッションレコード変換テスト"""
        now = datetime.now()
        data = {
            "timestamp": now.isoformat(),
            "session_type": TimerState.WORK,
            "completed": True,
            "duration_minutes": 25
        }
        record = SessionRecord.from_dict(data)
        assert record.timestamp.replace(microsecond=0) == now.replace(microsecond=0)
        assert record.session_type == TimerState.WORK
        assert record.completed is True
        assert record.duration_minutes == 25


class TestDailyStats:
    """DailyStats データクラスのテスト"""

    def test_daily_stats_creation(self):
        """統計データの作成テスト"""
        stats = DailyStats(
            date=date.today(),
            completed_work_sessions=4,
            completed_break_sessions=3,
            total_work_minutes=100,
            total_break_minutes=15
        )
        assert stats.date == date.today()
        assert stats.completed_work_sessions == 4
        assert stats.completed_break_sessions == 3
        assert stats.total_work_minutes == 100
        assert stats.total_break_minutes == 15

    def test_daily_stats_zero_sessions(self):
        """セッション0の統計テスト"""
        stats = DailyStats(
            date=date.today(),
            completed_work_sessions=0,
            completed_break_sessions=0,
            total_work_minutes=0,
            total_break_minutes=0
        )
        assert stats.completed_work_sessions == 0
        assert stats.total_work_minutes == 0

    def test_daily_stats_to_dict(self):
        """統計データ→辞書変換テスト"""
        stats = DailyStats(
            date=date.today(),
            completed_work_sessions=2,
            completed_break_sessions=1,
            total_work_minutes=50,
            total_break_minutes=5
        )
        data = stats.to_dict()
        assert data["date"] == date.today().isoformat()
        assert data["completed_work_sessions"] == 2
        assert data["completed_break_sessions"] == 1
        assert data["total_work_minutes"] == 50
        assert data["total_break_minutes"] == 5


class TestInMemoryRepository:
    """InMemoryRepository のテスト"""

    def test_repository_creation(self):
        """リポジトリの作成テスト"""
        repo = InMemoryRepository()
        assert repo is not None

    def test_add_session(self):
        """セッション追加テスト"""
        repo = InMemoryRepository()
        record = SessionRecord(
            timestamp=datetime.now(),
            session_type=TimerState.WORK,
            completed=True,
            duration_minutes=25
        )
        repo.add_session(record)
        sessions = repo.get_today_sessions()
        assert len(sessions) == 1
        assert sessions[0].session_type == TimerState.WORK

    def test_add_multiple_sessions(self):
        """複数セッション追加テスト"""
        repo = InMemoryRepository()
        now = datetime.now()
        
        # 3つのセッションを追加
        for i in range(3):
            record = SessionRecord(
                timestamp=now + timedelta(minutes=i),
                session_type=TimerState.WORK,
                completed=True,
                duration_minutes=25
            )
            repo.add_session(record)
        
        sessions = repo.get_today_sessions()
        assert len(sessions) == 3

    def test_get_today_sessions_empty(self):
        """本日のセッション取得（空）テスト"""
        repo = InMemoryRepository()
        sessions = repo.get_today_sessions()
        assert sessions == []

    def test_get_today_sessions_filters_old_dates(self):
        """本日のセッション取得（過去日除外）テスト"""
        repo = InMemoryRepository()
        
        # 昨日のセッション
        yesterday = datetime.now() - timedelta(days=1)
        old_record = SessionRecord(
            timestamp=yesterday,
            session_type=TimerState.WORK,
            completed=True,
            duration_minutes=25
        )
        repo.add_session(old_record)
        
        # 今日のセッション
        today_record = SessionRecord(
            timestamp=datetime.now(),
            session_type=TimerState.WORK,
            completed=True,
            duration_minutes=25
        )
        repo.add_session(today_record)
        
        # 今日のセッションのみ取得
        sessions = repo.get_today_sessions()
        assert len(sessions) == 1
        assert sessions[0].timestamp.date() == date.today()

    def test_get_sessions_by_date_range(self):
        """日付範囲でセッション取得テスト"""
        repo = InMemoryRepository()
        now = datetime.now()
        
        # 3日間のセッションを追加
        for i in range(3):
            record = SessionRecord(
                timestamp=now - timedelta(days=i),
                session_type=TimerState.WORK,
                completed=True,
                duration_minutes=25
            )
            repo.add_session(record)
        
        # 最近2日間を取得
        start_date = date.today() - timedelta(days=1)
        end_date = date.today()
        sessions = repo.get_sessions_by_date_range(start_date, end_date)
        assert len(sessions) == 2

    def test_clear_sessions(self):
        """セッションクリアテスト"""
        repo = InMemoryRepository()
        record = SessionRecord(
            timestamp=datetime.now(),
            session_type=TimerState.WORK,
            completed=True,
            duration_minutes=25
        )
        repo.add_session(record)
        assert len(repo.get_today_sessions()) == 1
        
        # クリア
        repo.clear()
        assert len(repo.get_today_sessions()) == 0


class TestSessionManager:
    """SessionManager のテスト"""

    def test_manager_creation(self):
        """マネージャーの作成テスト"""
        repo = InMemoryRepository()
        manager = SessionManager(repo)
        assert manager is not None

    def test_complete_work_session(self):
        """作業セッション完了記録テスト"""
        repo = InMemoryRepository()
        manager = SessionManager(repo)
        
        manager.complete_session(TimerState.WORK, duration_minutes=25)
        sessions = repo.get_today_sessions()
        
        assert len(sessions) == 1
        assert sessions[0].session_type == TimerState.WORK
        assert sessions[0].completed is True

    def test_complete_break_session(self):
        """休憩セッション完了記録テスト"""
        repo = InMemoryRepository()
        manager = SessionManager(repo)
        
        manager.complete_session(TimerState.BREAK, duration_minutes=5)
        sessions = repo.get_today_sessions()
        
        assert len(sessions) == 1
        assert sessions[0].session_type == TimerState.BREAK

    def test_get_today_stats_empty(self):
        """本日の統計取得（空）テスト"""
        repo = InMemoryRepository()
        manager = SessionManager(repo)
        
        stats = manager.get_today_stats()
        assert stats.completed_work_sessions == 0
        assert stats.completed_break_sessions == 0
        assert stats.total_work_minutes == 0
        assert stats.total_break_minutes == 0

    def test_get_today_stats_with_sessions(self):
        """本日の統計取得（セッションあり）テスト"""
        repo = InMemoryRepository()
        manager = SessionManager(repo)
        
        # 作業セッション2回
        manager.complete_session(TimerState.WORK, duration_minutes=25)
        manager.complete_session(TimerState.WORK, duration_minutes=25)
        
        # 休憩セッション1回
        manager.complete_session(TimerState.BREAK, duration_minutes=5)
        
        stats = manager.get_today_stats()
        assert stats.completed_work_sessions == 2
        assert stats.completed_break_sessions == 1
        assert stats.total_work_minutes == 50
        assert stats.total_break_minutes == 5

    def test_get_today_stats_ignores_incomplete(self):
        """本日の統計取得（未完了除外）テスト"""
        repo = InMemoryRepository()
        manager = SessionManager(repo)
        
        # 完了セッション
        manager.complete_session(TimerState.WORK, duration_minutes=25)
        
        # 未完了セッション（手動追加）
        incomplete_record = SessionRecord(
            timestamp=datetime.now(),
            session_type=TimerState.WORK,
            completed=False,
            duration_minutes=0
        )
        repo.add_session(incomplete_record)
        
        stats = manager.get_today_stats()
        # 完了したものだけカウント
        assert stats.completed_work_sessions == 1

    def test_reset_today(self):
        """本日の統計リセットテスト"""
        repo = InMemoryRepository()
        manager = SessionManager(repo)
        
        # セッションを記録
        manager.complete_session(TimerState.WORK, duration_minutes=25)
        assert len(repo.get_today_sessions()) == 1
        
        # リセット
        manager.reset_today()
        
        # 本日のセッションがクリアされる
        sessions = repo.get_today_sessions()
        assert len(sessions) == 0

    def test_multiple_work_sessions(self):
        """複数の作業セッション統計テスト"""
        repo = InMemoryRepository()
        manager = SessionManager(repo)
        
        # 4セッション完了
        for _ in range(4):
            manager.complete_session(TimerState.WORK, duration_minutes=25)
        
        stats = manager.get_today_stats()
        assert stats.completed_work_sessions == 4
        assert stats.total_work_minutes == 100

    def test_long_break_session(self):
        """長休憩セッション記録テスト"""
        repo = InMemoryRepository()
        manager = SessionManager(repo)
        
        manager.complete_session(TimerState.LONG_BREAK, duration_minutes=15)
        
        stats = manager.get_today_stats()
        # 長休憩も休憩としてカウント
        assert stats.completed_break_sessions == 1
        assert stats.total_break_minutes == 15
