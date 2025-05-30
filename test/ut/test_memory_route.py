from io import BytesIO
import json
from unittest.mock import Mock, patch

import pytest

from weaver.server.routes.memory_route import memory_bp


@pytest.fixture
def client():
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(memory_bp)
    app.config['TESTING'] = True
    return app.test_client()


class TestMemoryRoute:
    
    @patch('weaver.server.routes.memory_route.MemoryService')
    @patch('weaver.server.routes.memory_route.validate_memory_data')
    def test_create_memory_json_success(self, mock_validate, mock_memory_service, client):
        # Setup
        mock_validate.return_value = None
        mock_service_instance = Mock()
        mock_memory = {"id": "mem123", "tripName": "Test Trip"}
        mock_service_instance.create_memory.return_value = mock_memory
        mock_memory_service.return_value = mock_service_instance
        
        # Execute
        response = client.post(
            '/memories',
            data=json.dumps({
                "tripName": "Test Trip",
                "startDate": "2024-01-01",
                "endDate": "2024-01-02",
                "location": "Test Location",
                "notes": "Test notes",
                "music": "Test music"
            }),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['memory']['id'] == "mem123"

    @patch('weaver.server.routes.memory_route.MemoryService')
    @patch('weaver.server.routes.memory_route.validate_memory_data')
    @patch('weaver.server.routes.memory_route.handle_uploaded_files')
    def test_create_memory_form_data_success(self, mock_handle_files, mock_validate, mock_memory_service, client):
        # Setup
        mock_validate.return_value = None
        mock_handle_files.return_value = [{"filename": "test.jpg", "file_id": "file123"}]
        mock_service_instance = Mock()
        mock_memory = {"id": "mem123", "tripName": "Test Trip"}
        mock_service_instance.create_memory.return_value = mock_memory
        mock_memory_service.return_value = mock_service_instance
        
        # Execute
        response = client.post(
            '/memories',
            data={
                'trip-name': 'Test Trip',
                'trip-start-date': '2024-01-01',
                'trip-end-date': '2024-01-02',
                'memory-location': 'Test Location',
                'memory-text': 'Test notes',
                'memory-music': 'Test music',
                'memory-photos': (BytesIO(b'fake image data'), 'test.jpg')
            },
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['memory']['id'] == "mem123"

    @patch('weaver.server.routes.memory_route.validate_memory_data')
    def test_create_memory_validation_error(self, mock_validate, client):
        # Setup
        mock_validate.return_value = "Missing required fields"
        
        # Execute
        response = client.post(
            '/memories',
            data=json.dumps({"tripName": ""}),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error'] == "Missing required fields"

    def test_create_memory_no_data(self, client):
        # Execute
        response = client.post('/memories')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert "请提供有效数据" in data['error']

    @patch('weaver.server.routes.memory_route.MemoryService')
    def test_get_memory_success(self, mock_memory_service, client):
        # Setup
        mock_service_instance = Mock()
        mock_memory = {
            "id": "mem123",
            "tripName": "Test Trip",
            "location": "Test Location"
        }
        mock_service_instance.get_memory_by_id.return_value = mock_memory
        mock_memory_service.return_value = mock_service_instance
        
        # Execute
        response = client.get('/memories/mem123')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['memory']['id'] == "mem123"
        mock_service_instance.get_memory_by_id.assert_called_once_with("mem123")

    @patch('weaver.server.routes.memory_route.MemoryService')
    def test_get_memory_not_found(self, mock_memory_service, client):
        # Setup
        mock_service_instance = Mock()
        mock_service_instance.get_memory_by_id.return_value = None
        mock_memory_service.return_value = mock_service_instance
        
        # Execute
        response = client.get('/memories/mem123')
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert "记忆未找到" in data['error']

    @patch('weaver.server.routes.memory_route.MemoryService')
    def test_get_memory_album_success(self, mock_memory_service, client):
        # Setup
        mock_service_instance = Mock()
        mock_album = {
            "items": [{"type": "note", "title": "Test Note"}],
            "count": 1
        }
        mock_service_instance.get_memory_album.return_value = mock_album
        mock_memory_service.return_value = mock_service_instance
        
        # Execute
        response = client.get('/memories/mem123/album')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['album']['count'] == 1
        mock_service_instance.get_memory_album.assert_called_once_with("mem123")

    @patch('weaver.server.routes.memory_route.MemoryService')
    def test_get_memory_album_not_found(self, mock_memory_service, client):
        # Setup
        mock_service_instance = Mock()
        mock_service_instance.get_memory_album.return_value = None
        mock_memory_service.return_value = mock_service_instance
        
        # Execute
        response = client.get('/memories/mem123/album')
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert "记忆未找到" in data['error']

    @patch('weaver.server.routes.memory_route.MemoryService')
    def test_create_memory_exception(self, mock_memory_service, client):
        # Setup
        mock_memory_service.side_effect = Exception("Service error")
        
        # Execute
        response = client.post(
            '/memories',
            data=json.dumps({"tripName": "Test"}),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert "创建记忆失败" in data['error']
