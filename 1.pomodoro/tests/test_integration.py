"""
統合テスト

APIエンドポイント間の統合テストとエンドツーエンドのシナリオテスト
"""

import pytest
import time
from flask import json


class TestTimerAPIIntegration:
    """タイマーAPI統合テスト"""
    
    def test_timer_start_and_status_integration(self, client):
        """タイマー開始と状態取得の統合テスト"""
        # タイマーを開始
        start_response = client.post('/api/timer/start')
        assert start_response.status_code == 200
        
        start_data = json.loads(start_response.data)
        assert start_data['success'] is True
        assert start_data['state'] == 'work'
        
        # 状態を取得
        status_response = client.get('/api/timer/status')
        assert status_response.status_code == 200
        
        status_data = json.loads(status_response.data)
        assert status_data['state'] == 'work'
        assert status_data['is_paused'] is False
    
    def test_timer_multiple_status_checks(self, client):
        """タイマー開始後の複数回の状態確認"""
        # タイマーを開始
        client.post('/api/timer/start')
        
        # 複数回状態を確認
        for _ in range(3):
            response = client.get('/api/timer/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['state'] == 'work'
    
    def test_timer_restart_resets_state(self, client):
        """タイマーの再開始で状態がリセットされることを確認"""
        # 1回目の開始
        start1 = client.post('/api/timer/start')
        data1 = json.loads(start1.data)
        remaining1 = data1['remaining']
        
        # 少し待つ
        time.sleep(0.1)
        
        # 2回目の開始
        start2 = client.post('/api/timer/start')
        data2 = json.loads(start2.data)
        remaining2 = data2['remaining']
        
        # リセットされているので、2回目の方が残り時間が多いかほぼ同じ
        assert remaining2 >= remaining1 - 1  # 1秒の誤差を許容


class TestTimerAPIErrorHandling:
    """タイマーAPIのエラーハンドリングテスト"""
    
    def test_invalid_http_method_for_start(self, client):
        """start エンドポイントへの不正なHTTPメソッド"""
        # GETメソッドでアクセス（POSTが正しい）
        response = client.get('/api/timer/start')
        # Flask はデフォルトで405 Method Not Allowedを返す
        assert response.status_code == 405
    
    def test_invalid_http_method_for_status(self, client):
        """status エンドポイントへの不正なHTTPメソッド"""
        # POSTメソッドでアクセス（GETが正しい）
        response = client.post('/api/timer/status')
        # Flask はデフォルトで405 Method Not Allowedを返す
        assert response.status_code == 405
    
    def test_nonexistent_endpoint(self, client):
        """存在しないAPIエンドポイント"""
        response = client.get('/api/timer/nonexistent')
        assert response.status_code == 404


class TestWebAndAPIIntegration:
    """WebページとAPIの統合テスト"""
    
    def test_index_page_loads_before_api_call(self, client):
        """API呼び出し前にインデックスページが読み込めることを確認"""
        response = client.get('/')
        assert response.status_code == 200
        # ページタイトルは日本語: ポモドーロタイマー
        assert 'ポモドーロタイマー'.encode('utf-8') in response.data
    
    def test_index_page_and_api_combination(self, client):
        """インデックスページとAPI呼び出しの組み合わせ"""
        # まずWebページにアクセス
        web_response = client.get('/')
        assert web_response.status_code == 200
        
        # タイマーを開始
        api_response = client.post('/api/timer/start')
        assert api_response.status_code == 200
        
        # 状態を確認
        status_response = client.get('/api/timer/status')
        assert status_response.status_code == 200
    
    def test_health_check_and_timer_api(self, client):
        """ヘルスチェックとタイマーAPIの組み合わせ"""
        # ヘルスチェック
        health_response = client.get('/health')
        assert health_response.status_code == 200
        health_data = json.loads(health_response.data)
        assert health_data['status'] == 'ok'
        
        # タイマーAPI
        timer_response = client.post('/api/timer/start')
        assert timer_response.status_code == 200


class TestEndToEndScenarios:
    """エンドツーエンドのシナリオテスト"""
    
    def test_complete_pomodoro_workflow(self, client):
        """完全なポモドーロワークフロー"""
        # 1. Webページにアクセス
        index_response = client.get('/')
        assert index_response.status_code == 200
        
        # 2. 初期状態を確認
        initial_status = client.get('/api/timer/status')
        initial_data = json.loads(initial_status.data)
        assert initial_data['state'] == 'stopped'
        
        # 3. タイマーを開始
        start_response = client.post('/api/timer/start')
        start_data = json.loads(start_response.data)
        assert start_data['success'] is True
        assert start_data['state'] == 'work'
        
        # 4. 実行中の状態を確認
        running_status = client.get('/api/timer/status')
        running_data = json.loads(running_status.data)
        assert running_data['state'] == 'work'
        assert running_data['is_paused'] is False
    
    def test_multiple_timer_cycles(self, client):
        """複数のタイマーサイクル"""
        # サイクル1
        client.post('/api/timer/start')
        status1 = client.get('/api/timer/status')
        data1 = json.loads(status1.data)
        assert data1['state'] == 'work'
        
        # サイクル2
        client.post('/api/timer/start')
        status2 = client.get('/api/timer/status')
        data2 = json.loads(status2.data)
        assert data2['state'] == 'work'
        
        # サイクル3
        client.post('/api/timer/start')
        status3 = client.get('/api/timer/status')
        data3 = json.loads(status3.data)
        assert data3['state'] == 'work'


class TestConcurrentAPIAccess:
    """並行APIアクセステスト"""
    
    def test_concurrent_status_checks(self, client):
        """並行した状態確認"""
        # タイマーを開始
        client.post('/api/timer/start')
        
        # 複数回並行して状態を確認（シミュレート）
        responses = []
        for _ in range(5):
            response = client.get('/api/timer/status')
            responses.append(response)
        
        # すべて成功することを確認
        for response in responses:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'state' in data
    
    def test_status_check_without_start(self, client):
        """開始せずに状態確認"""
        # タイマーを開始せずに状態を確認
        response = client.get('/api/timer/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['state'] == 'stopped'
        assert data['is_paused'] is False
        assert data['is_completed'] is False


class TestAPIResponseConsistency:
    """APIレスポンスの一貫性テスト"""
    
    def test_start_response_consistency(self, client):
        """startレスポンスの一貫性"""
        # 複数回開始して、レスポンス構造が一貫していることを確認
        for _ in range(3):
            response = client.post('/api/timer/start')
            data = json.loads(response.data)
            
            # 必須フィールドが存在することを確認
            assert 'success' in data
            assert 'state' in data
            assert 'remaining' in data
            assert 'display_time' in data
            
            # データ型を確認
            assert isinstance(data['success'], bool)
            assert isinstance(data['state'], str)
            assert isinstance(data['remaining'], int)
            assert isinstance(data['display_time'], str)
    
    def test_status_response_consistency(self, client):
        """statusレスポンスの一貫性"""
        # タイマーを開始
        client.post('/api/timer/start')
        
        # 複数回状態確認して、レスポンス構造が一貫していることを確認
        for _ in range(3):
            response = client.get('/api/timer/status')
            data = json.loads(response.data)
            
            # 必須フィールドが存在することを確認
            assert 'state' in data
            assert 'remaining' in data
            assert 'display_time' in data
            assert 'progress' in data
            assert 'is_paused' in data
            assert 'is_completed' in data
            
            # データ型を確認
            assert isinstance(data['state'], str)
            assert isinstance(data['remaining'], int)
            assert isinstance(data['display_time'], str)
            assert isinstance(data['progress'], (int, float))
            assert isinstance(data['is_paused'], bool)
            assert isinstance(data['is_completed'], bool)


class TestAPIDataValidation:
    """APIデータ検証テスト"""
    
    def test_remaining_time_is_non_negative(self, client):
        """残り時間が非負であることを確認"""
        client.post('/api/timer/start')
        
        for _ in range(5):
            response = client.get('/api/timer/status')
            data = json.loads(response.data)
            assert data['remaining'] >= 0
    
    def test_progress_is_in_valid_range(self, client):
        """進捗率が有効範囲内であることを確認"""
        client.post('/api/timer/start')
        
        for _ in range(5):
            response = client.get('/api/timer/status')
            data = json.loads(response.data)
            assert 0.0 <= data['progress'] <= 1.0
    
    def test_display_time_format_is_valid(self, client):
        """表示時間のフォーマットが有効であることを確認"""
        client.post('/api/timer/start')
        
        response = client.get('/api/timer/status')
        data = json.loads(response.data)
        
        # MM:SS形式であることを確認
        display_time = data['display_time']
        parts = display_time.split(':')
        assert len(parts) == 2
        
        # 各パートが数値であることを確認
        minutes, seconds = parts
        assert minutes.isdigit()
        assert seconds.isdigit()
        
        # 秒が0-59の範囲であることを確認
        assert 0 <= int(seconds) <= 59


class TestStaticFilesAndAPI:
    """静的ファイルとAPIの統合テスト"""
    
    def test_static_css_and_api_access(self, client):
        """CSSファイルとAPIの両方にアクセス"""
        # CSSファイルにアクセス
        css_response = client.get('/static/css/style.css')
        assert css_response.status_code == 200
        
        # APIにアクセス
        api_response = client.post('/api/timer/start')
        assert api_response.status_code == 200
    
    def test_multiple_resource_types(self, client):
        """複数のリソースタイプへのアクセス"""
        # Webページ
        web_response = client.get('/')
        assert web_response.status_code == 200
        
        # ヘルスチェック
        health_response = client.get('/health')
        assert health_response.status_code == 200
        
        # タイマーAPI
        timer_response = client.post('/api/timer/start')
        assert timer_response.status_code == 200
        
        # 静的ファイル
        static_response = client.get('/static/css/style.css')
        assert static_response.status_code == 200
