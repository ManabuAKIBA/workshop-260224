"""セッションデータの永続化を担当するリポジトリ"""
from abc import ABC, abstractmethod
from typing import List
from datetime import date, datetime
import json
import os
from pathlib import Path


class SessionRepository(ABC):
    """
    セッションデータ永続化の抽象インターフェース
    
    依存性注入のために抽象化し、テスト用と本番用で実装を切り替え可能にする
    """
    
    @abstractmethod
    def add_session(self, record: 'SessionRecord') -> None:
        """
        セッション記録を追加
        
        Args:
            record: 追加するセッション記録
        """
        pass
    
    @abstractmethod
    def get_today_sessions(self) -> List['SessionRecord']:
        """
        本日のセッション記録を取得
        
        Returns:
            本日のセッション記録リスト
        """
        pass
    
    @abstractmethod
    def get_sessions_by_date_range(self, start_date: date, end_date: date) -> List['SessionRecord']:
        """
        指定期間のセッション記録を取得
        
        Args:
            start_date: 開始日
            end_date: 終了日
            
        Returns:
            指定期間のセッション記録リスト
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """全てのセッション記録を削除"""
        pass


class InMemoryRepository(SessionRepository):
    """
    メモリ内でセッションデータを管理するリポジトリ（テスト用）
    
    データは永続化されず、アプリケーション終了で消失する
    テスト実行時に使用する
    """
    
    def __init__(self):
        """リポジトリを初期化"""
        self._sessions: List['SessionRecord'] = []
    
    def add_session(self, record: 'SessionRecord') -> None:
        """セッション記録を追加"""
        self._sessions.append(record)
    
    def get_today_sessions(self) -> List['SessionRecord']:
        """本日のセッション記録を取得"""
        today = date.today()
        return [
            session for session in self._sessions
            if session.timestamp.date() == today
        ]
    
    def get_sessions_by_date_range(self, start_date: date, end_date: date) -> List['SessionRecord']:
        """指定期間のセッション記録を取得"""
        return [
            session for session in self._sessions
            if start_date <= session.timestamp.date() <= end_date
        ]
    
    def clear(self) -> None:
        """全てのセッション記録を削除"""
        self._sessions.clear()


class FileRepository(SessionRepository):
    """
    JSONファイルでセッションデータを管理するリポジトリ（本番用）
    
    データはJSONファイルに永続化される
    本番環境で使用する
    """
    
    def __init__(self, file_path: str):
        """
        リポジトリを初期化
        
        Args:
            file_path: データ保存先のJSONファイルパス
        """
        self.file_path = Path(file_path)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """データファイルが存在しない場合は作成"""
        if not self.file_path.exists():
            # ディレクトリを作成
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            # 空のJSONファイルを作成
            self._save_sessions([])
    
    def _load_sessions(self) -> List['SessionRecord']:
        """ファイルからセッション記録を読み込み"""
        # SessionRecord のインポートを遅延させる（循環インポート回避）
        from models.session import SessionRecord
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [SessionRecord.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_sessions(self, sessions: List['SessionRecord']) -> None:
        """セッション記録をファイルに保存"""
        data = [session.to_dict() for session in sessions]
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_session(self, record: 'SessionRecord') -> None:
        """セッション記録を追加"""
        sessions = self._load_sessions()
        sessions.append(record)
        self._save_sessions(sessions)
    
    def get_today_sessions(self) -> List['SessionRecord']:
        """本日のセッション記録を取得"""
        sessions = self._load_sessions()
        today = date.today()
        return [
            session for session in sessions
            if session.timestamp.date() == today
        ]
    
    def get_sessions_by_date_range(self, start_date: date, end_date: date) -> List['SessionRecord']:
        """指定期間のセッション記録を取得"""
        sessions = self._load_sessions()
        return [
            session for session in sessions
            if start_date <= session.timestamp.date() <= end_date
        ]
    
    def clear(self) -> None:
        """全てのセッション記録を削除"""
        self._save_sessions([])
