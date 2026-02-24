"""
タイマーAPIエンドポイントのテスト
"""

import pytest
from flask import json


class TestTimerStartAPI:
    """POST /api/timer/start のテスト"""
    
    def test_start_endpoint_exists(self, client):
        """エンドポイントが存在することを確認"""
        response = client.post('/api/timer/start')
        assert response.status_code == 200
    
    def test_start_returns_json(self, client):
        """JSONレスポンスが返ることを確認"""
        response = client.post('/api/timer/start')
        assert response.content_type == 'application/json'
    
    def test_start_response_structure(self, client):
        """レスポンス構造を確認"""
        response = client.post('/api/timer/start')
        data = json.loads(response.data)
        
        assert 'success' in data
        assert 'state' in data
        assert 'remaining' in data
        assert 'display_time' in data
    
    def test_start_success_flag(self, client):
        """成功フラグがTrueであることを確認"""
        response = client.post('/api/timer/start')
        data = json.loads(response.data)
        
        assert data['success'] is True
    
    def test_start_sets_work_state(self, client):
        """作業状態が設定されることを確認"""
        response = client.post('/api/timer/start')
        data = json.loads(response.data)
        
        assert data['state'] == 'work'
    
    def test_start_sets_remaining_time(self, client):
        """残り時間が設定されることを確認（デフォルト25分=1500秒）"""
        response = client.post('/api/timer/start')
        data = json.loads(response.data)
        
        assert data['remaining'] == 1500
    
    def test_start_display_time_format(self, client):
        """表示時間がMM:SS形式であることを確認"""
        response = client.post('/api/timer/start')
        data = json.loads(response.data)
        
        assert data['display_time'] == '25:00'


class TestTimerStatusAPI:
    """GET /api/timer/status のテスト"""
    
    def test_status_endpoint_exists(self, client):
        """エンドポイントが存在することを確認"""
        response = client.get('/api/timer/status')
        assert response.status_code == 200
    
    def test_status_returns_json(self, client):
        """JSONレスポンスが返ることを確認"""
        response = client.get('/api/timer/status')
        assert response.content_type == 'application/json'
    
    def test_status_response_structure(self, client):
        """レスポンス構造を確認"""
        response = client.get('/api/timer/status')
        data = json.loads(response.data)
        
        assert 'state' in data
        assert 'remaining' in data
        assert 'display_time' in data
        assert 'progress' in data
        assert 'is_paused' in data
        assert 'is_completed' in data
    
    def test_status_before_start(self, client):
        """開始前の状態を確認"""
        response = client.get('/api/timer/status')
        data = json.loads(response.data)
        
        assert data['state'] == 'stopped'
        assert data['is_paused'] is False
        assert data['is_completed'] is False
    
    def test_status_after_start(self, client):
        """開始後の状態を確認"""
        # タイマーを開始
        client.post('/api/timer/start')
        
        # 状態を取得
        response = client.get('/api/timer/status')
        data = json.loads(response.data)
        
        assert data['state'] == 'work'
        assert data['remaining'] <= 1500
        assert data['is_paused'] is False
        assert data['is_completed'] is False
    
    def test_status_progress_range(self, client):
        """進捗率が0.0～1.0の範囲であることを確認"""
        response = client.get('/api/timer/status')
        data = json.loads(response.data)
        
        assert 0.0 <= data['progress'] <= 1.0


class TestTimerAPIIntegration:
    """タイマーAPIの統合テスト"""
    
    def test_start_and_check_status(self, client):
        """開始してから状態を確認する一連の流れ"""
        # タイマーを開始
        start_response = client.post('/api/timer/start')
        start_data = json.loads(start_response.data)
        
        assert start_data['success'] is True
        assert start_data['state'] == 'work'
        
        # 状態を確認
        status_response = client.get('/api/timer/status')
        status_data = json.loads(status_response.data)
        
        assert status_data['state'] == 'work'
        assert status_data['remaining'] <= 1500
    
    def test_multiple_starts_reset_timer(self, client, app):
        """複数回開始すると、タイマーがリセットされることを確認"""
        # 1回目の開始
        client.post('/api/timer/start')
        
        # MockClockで時間を進める
        app.clock.advance(5.0)
        status1 = client.get('/api/timer/status')
        data1 = json.loads(status1.data)
        
        # 2回目の開始
        client.post('/api/timer/start')
        status2 = client.get('/api/timer/status')
        data2 = json.loads(status2.data)
        
        # 2回目の方が残り時間が多いはず（リセットされた）
        assert data2['remaining'] >= data1['remaining']
