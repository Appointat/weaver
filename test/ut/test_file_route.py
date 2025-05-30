from io import BytesIO
import json
from unittest.mock import patch

import pytest

from weaver.server.routes.file_route import file_bp


@pytest.fixture
def client():
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(file_bp)
    app.config['TESTING'] = True
    return app.test_client()


class TestFileRoute:
    
    @patch('weaver.server.routes.file_route.save_uploaded_file')
    @patch('weaver.server.routes.file_route.allowed_file')
    def test_upload_files_success(self, mock_allowed_file, mock_save_file, client):
        # Setup
        mock_allowed_file.return_value = True
        mock_save_file.return_value = {
            "filename": "test.jpg",
            "file_id": "file123"
        }
        
        # Execute
        response = client.post(
            '/files/upload',
            data={
                'files': (BytesIO(b'fake image data'), 'test.jpg')
            },
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] == 1
        assert data['file_ids'] == ["file123"]
        mock_save_file.assert_called_once()

    @patch('weaver.server.routes.file_route.save_uploaded_file')
    @patch('weaver.server.routes.file_route.allowed_file')
    def test_upload_multiple_files_success(self, mock_allowed_file, mock_save_file, client):
        # Setup
        mock_allowed_file.return_value = True
        mock_save_file.side_effect = [
            {"filename": "test1.jpg", "file_id": "file123"},
            {"filename": "test2.jpg", "file_id": "file456"}
        ]
        
        # Execute
        response = client.post(
            '/files/upload',
            data={
                'files': [
                    (BytesIO(b'fake image data 1'), 'test1.jpg'),
                    (BytesIO(b'fake image data 2'), 'test2.jpg')
                ]
            },
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] == 2
        assert data['file_ids'] == ["file123", "file456"]
        assert mock_save_file.call_count == 2

    def test_upload_files_no_files_key(self, client):
        # Execute
        response = client.post(
            '/files/upload',
            data={},
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert "没有文件被上传" in data['error']

    def test_upload_files_empty_filename(self, client):
        # Execute
        response = client.post(
            '/files/upload',
            data={
                'files': (BytesIO(b''), '')
            },
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert "没有选择文件" in data['error']

    @patch('weaver.server.routes.file_route.allowed_file')
    def test_upload_files_invalid_file_type(self, mock_allowed_file, client):
        # Setup
        mock_allowed_file.return_value = False
        
        # Execute
        response = client.post(
            '/files/upload',
            data={
                'files': (BytesIO(b'fake data'), 'test.exe')
            },
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert "没有有效文件被上传" in data['error']

    @patch('weaver.server.routes.file_route.save_uploaded_file')
    @patch('weaver.server.routes.file_route.allowed_file')
    def test_upload_files_save_error(self, mock_allowed_file, mock_save_file, client):
        # Setup
        mock_allowed_file.return_value = True
        mock_save_file.side_effect = Exception("Save error")
        
        # Execute
        response = client.post(
            '/files/upload',
            data={
                'files': (BytesIO(b'fake image data'), 'test.jpg')
            },
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert "没有有效文件被上传" in data['error']

    @patch('weaver.server.routes.file_route.save_uploaded_file')
    @patch('weaver.server.routes.file_route.allowed_file')
    def test_upload_files_partial_success(self, mock_allowed_file, mock_save_file, client):
        # Setup
        mock_allowed_file.return_value = True
        mock_save_file.side_effect = [
            {"filename": "test1.jpg", "file_id": "file123"},
            Exception("Save error for second file")
        ]
        
        # Execute
        response = client.post(
            '/files/upload',
            data={
                'files': [
                    (BytesIO(b'fake image data 1'), 'test1.jpg'),
                    (BytesIO(b'fake image data 2'), 'test2.jpg')
                ]
            },
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] == 1
        assert data['file_ids'] == ["file123"]

    @patch('weaver.server.routes.file_route.allowed_file')
    def test_upload_files_general_exception(self, mock_allowed_file, client):
        # Setup
        mock_allowed_file.side_effect = Exception("General error")
        
        # Execute
        response = client.post(
            '/files/upload',
            data={
                'files': (BytesIO(b'fake image data'), 'test.jpg')
            },
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert "文件上传失败" in data['error']
