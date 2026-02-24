"""
Flaskアプリケーションの基本動作テスト
"""

import pytest
from flask import Flask


class TestAppCreation:
    """Flaskアプリケーションの作成テスト"""
    
    def test_app_creation(self, app):
        """アプリケーションが正常に作成されることを確認"""
        assert app is not None
        assert isinstance(app, Flask)
    
    def test_app_is_testing(self, app):
        """テスト環境が正しく設定されていることを確認"""
        assert app.config['TESTING'] is True
    
    def test_app_debug_in_testing(self, app):
        """テスト環境でDEBUGモードが有効になっていることを確認"""
        assert app.config['DEBUG'] is True
    
    def test_secret_key_is_set(self, app):
        """SECRET_KEYが設定されていることを確認"""
        assert app.config['SECRET_KEY'] is not None
        assert app.config['SECRET_KEY'] != ''


class TestAppConfiguration:
    """Flaskアプリケーションの設定テスト"""
    
    def test_development_config(self):
        """開発環境の設定が正しいことを確認"""
        from app import create_app
        app = create_app('development')
        
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is False
    
    def test_testing_config(self):
        """テスト環境の設定が正しいことを確認"""
        from app import create_app
        app = create_app('testing')
        
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is True
    
    def test_default_config(self):
        """デフォルト設定が開発環境になることを確認"""
        from app import create_app
        app = create_app()
        
        # デフォルトは開発環境
        assert app.config['DEBUG'] is True


class TestDataDirectory:
    """データディレクトリの作成テスト"""
    
    def test_data_directory_exists(self, app):
        """データディレクトリが存在することを確認"""
        data_dir = app.config['DATA_DIR']
        assert data_dir.exists()
        assert data_dir.is_dir()
    
    def test_data_directory_path(self, app):
        """データディレクトリのパスが正しいことを確認"""
        data_dir = app.config['DATA_DIR']
        assert 'test_data' in str(data_dir)
