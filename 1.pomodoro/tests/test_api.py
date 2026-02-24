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
    
    def test_multiple_starts_reset_timer(self, client):
        """複数回開始すると、タイマーがリセットされることを確認"""
        # 1回目の開始
        client.post('/api/timer/start')
        
        # 少し待って状態確認
        import time
        time.sleep(0.1)
        status1 = client.get('/api/timer/status')
        data1 = json.loads(status1.data)
        
        # 2回目の開始
        client.post('/api/timer/start')
        status2 = client.get('/api/timer/status')
        data2 = json.loads(status2.data)
        
        # 2回目の方が残り時間が多いはず（リセットされた）
        assert data2['remaining'] >= data1['remaining']


class TestSessionTodayAPI:
    """GET /api/session/today のテスト"""
    
    def test_today_stats_endpoint_exists(self, client):
        """エンドポイントが存在することを確認"""
        response = client.get('/api/session/today')
        assert response.status_code == 200
    
    def test_today_stats_returns_json(self, client):
        """JSONレスポンスが返ることを確認"""
        response = client.get('/api/session/today')
        assert response.content_type == 'application/json'
    
    def test_today_stats_response_structure(self, client):
        """レスポンス構造を確認"""
        response = client.get('/api/session/today')
        data = json.loads(response.data)
        
        assert 'date' in data
        assert 'completed_work_sessions' in data
        assert 'completed_break_sessions' in data
        assert 'total_work_minutes' in data
        assert 'total_break_minutes' in data
    
    def test_today_stats_initial_values(self, client):
        """初期状態の統計値を確認"""
        response = client.get('/api/session/today')
        data = json.loads(response.data)
        
        # 初期状態では全てゼロ
        assert data['completed_work_sessions'] == 0
        assert data['completed_break_sessions'] == 0
        assert data['total_work_minutes'] == 0
        assert data['total_break_minutes'] == 0


class TestSessionCompleteAPI:
    """POST /api/session/complete のテスト"""
    
    def test_complete_endpoint_exists(self, client):
        """エンドポイントが存在することを確認"""
        response = client.post('/api/session/complete', 
                              json={
                                  'session_type': 'work',
                                  'duration_minutes': 25
                              })
        assert response.status_code == 200
    
    def test_complete_returns_json(self, client):
        """JSONレスポンスが返ることを確認"""
        response = client.post('/api/session/complete',
                              json={
                                  'session_type': 'work',
                                  'duration_minutes': 25
                              })
        assert response.content_type == 'application/json'
    
    def test_complete_response_structure(self, client):
        """レスポンス構造を確認"""
        response = client.post('/api/session/complete',
                              json={
                                  'session_type': 'work',
                                  'duration_minutes': 25
                              })
        data = json.loads(response.data)
        
        assert 'success' in data
        assert 'message' in data
    
    def test_complete_success_flag(self, client):
        """成功フラグがTrueであることを確認"""
        response = client.post('/api/session/complete',
                              json={
                                  'session_type': 'work',
                                  'duration_minutes': 25
                              })
        data = json.loads(response.data)
        
        assert data['success'] is True
    
    def test_complete_without_session_type(self, client):
        """session_typeなしでエラーを確認"""
        response = client.post('/api/session/complete',
                              json={
                                  'duration_minutes': 25
                              })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_complete_without_duration(self, client):
        """duration_minutesなしでエラーを確認"""
        response = client.post('/api/session/complete',
                              json={
                                  'session_type': 'work'
                              })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_complete_without_body(self, client):
        """リクエストボディなしでエラーを確認"""
        response = client.post('/api/session/complete',
                              data='',
                              content_type='application/json')
        # リクエストボディがないか、JSONパースできない場合は400
        assert response.status_code in [400, 415]


class TestSessionAPIIntegration:
    """セッションAPIの統合テスト"""
    
    def test_complete_and_check_stats(self, client):
        """セッション完了後に統計が更新されることを確認"""
        # 初期状態を確認
        stats_before = client.get('/api/session/today')
        data_before = json.loads(stats_before.data)
        assert data_before['completed_work_sessions'] == 0
        
        # セッション完了
        complete_response = client.post('/api/session/complete',
                                       json={
                                           'session_type': 'work',
                                           'duration_minutes': 25
                                       })
        complete_data = json.loads(complete_response.data)
        assert complete_data['success'] is True
        
        # 統計を確認
        stats_after = client.get('/api/session/today')
        data_after = json.loads(stats_after.data)
        
        assert data_after['completed_work_sessions'] == 1
        assert data_after['total_work_minutes'] == 25
    
    def test_multiple_sessions_accumulate(self, client):
        """複数のセッションが累積されることを確認"""
        # 作業セッション2回
        client.post('/api/session/complete',
                   json={
                       'session_type': 'work',
                       'duration_minutes': 25
                   })
        client.post('/api/session/complete',
                   json={
                       'session_type': 'work',
                       'duration_minutes': 25
                   })
        
        # 休憩セッション1回
        client.post('/api/session/complete',
                   json={
                       'session_type': 'break',
                       'duration_minutes': 5
                   })
        
        # 統計を確認
        stats = client.get('/api/session/today')
        data = json.loads(stats.data)
        
        assert data['completed_work_sessions'] == 2
        assert data['completed_break_sessions'] == 1
        assert data['total_work_minutes'] == 50
        assert data['total_break_minutes'] == 5
