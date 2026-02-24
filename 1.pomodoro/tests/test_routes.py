"""
Webルートのテスト
"""

import pytest
from flask import url_for


class TestIndexRoute:
    """メインページ（/）のテスト"""
    
    def test_index_status_code(self, client):
        """ステータスコードが200であることを確認"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_content_type(self, client):
        """コンテンツタイプがHTMLであることを確認"""
        response = client.get('/')
        assert response.content_type.startswith('text/html')
    
    def test_index_contains_title(self, client):
        """ページにタイトルが含まれることを確認"""
        response = client.get('/')
        assert 'ポモドーロタイマー' in response.data.decode('utf-8')
    
    def test_index_contains_timer_display(self, client):
        """タイマー表示要素が含まれることを確認"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'timerDisplay' in html
        assert '25:00' in html
    
    def test_index_contains_buttons(self, client):
        """開始・リセットボタンが含まれることを確認"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'startBtn' in html
        assert 'resetBtn' in html
        assert '開始' in html
        assert 'リセット' in html
    
    def test_index_contains_stats_section(self, client):
        """統計セクションが含まれることを確認"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '今日の進捗' in html
        assert 'sessionsCompleted' in html
        assert 'focusTime' in html
    
    def test_index_contains_css_links(self, client):
        """CSSファイルへのリンクが含まれることを確認"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'style.css' in html
        assert 'timer.css' in html
    
    def test_index_contains_progress_ring(self, client):
        """サーキュラープログレスのSVGが含まれることを確認"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert 'progress-ring' in html
        assert '<svg' in html
        assert '<circle' in html


class TestHealthRoute:
    """ヘルスチェックエンドポイント（/health）のテスト"""
    
    def test_health_status_code(self, client):
        """ステータスコードが200であることを確認"""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_content_type(self, client):
        """コンテンツタイプがJSONであることを確認"""
        response = client.get('/health')
        assert response.content_type == 'application/json'
    
    def test_health_response_structure(self, client):
        """レスポンス構造が正しいことを確認"""
        response = client.get('/health')
        data = response.get_json()
        
        assert 'status' in data
        assert 'message' in data
    
    def test_health_response_values(self, client):
        """レスポンスの値が正しいことを確認"""
        response = client.get('/health')
        data = response.get_json()
        
        assert data['status'] == 'ok'
        assert data['message'] == 'Application is running'


class TestStaticFiles:
    """静的ファイルのテスト"""
    
    def test_style_css_exists(self, client):
        """style.cssが存在することを確認"""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        assert 'text/css' in response.content_type
    
    def test_timer_css_exists(self, client):
        """timer.cssが存在することを確認"""
        response = client.get('/static/css/timer.css')
        assert response.status_code == 200
        assert 'text/css' in response.content_type
    
    def test_style_css_contains_container(self, client):
        """style.cssにコンテナスタイルが含まれることを確認"""
        response = client.get('/static/css/style.css')
        css = response.data.decode('utf-8')
        assert '.container' in css
    
    def test_timer_css_contains_progress(self, client):
        """timer.cssにプログレススタイルが含まれることを確認"""
        response = client.get('/static/css/timer.css')
        css = response.data.decode('utf-8')
        assert '.progress-ring' in css
        assert '.timer-display' in css


class TestNotFound:
    """存在しないページのテスト"""
    
    def test_404_status_code(self, client):
        """存在しないページで404が返ることを確認"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
