import json
from unittest.mock import Mock, patch

import pytest

from weaver.server.routes.chat_route import chat_bp


@pytest.fixture
def client():
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(chat_bp)
    app.config['TESTING'] = True
    return app.test_client()


class TestChatRoute:
    
    @patch('weaver.server.routes.chat_route.ChatService')
    @patch('weaver.server.routes.chat_route.validate_chat_message')
    def test_chat_with_memory_success(self, mock_validate, mock_chat_service, client):
        # Setup
        mock_validate.return_value = None
        mock_service_instance = Mock()
        mock_service_instance.submit_chat_with_memory.return_value = "job123"
        mock_chat_service.return_value = mock_service_instance
        
        # Execute
        response = client.post(
            '/memories/mem123/chat',
            data=json.dumps({"message": "Hello"}),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['response'] == "job123"
        mock_service_instance.submit_chat_with_memory.assert_called_once_with("Hello")

    @patch('weaver.server.routes.chat_route.validate_chat_message')
    def test_chat_with_memory_validation_error(self, mock_validate, client):
        # Setup
        mock_validate.return_value = "Invalid message"
        
        # Execute
        response = client.post(
            '/memories/mem123/chat',
            data=json.dumps({"message": ""}),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error'] == "Invalid message"

    @patch('weaver.server.routes.chat_route.ChatService')
    @patch('weaver.server.routes.chat_route.validate_chat_message')
    def test_chat_with_memory_not_found(self, mock_validate, mock_chat_service, client):
        # Setup
        mock_validate.return_value = None
        mock_service_instance = Mock()
        mock_service_instance.submit_chat_with_memory.return_value = None
        mock_chat_service.return_value = mock_service_instance
        
        # Execute
        response = client.post(
            '/memories/mem123/chat',
            data=json.dumps({"message": "Hello"}),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert "记忆未找到" in data['error']

    @patch('weaver.server.routes.chat_route.ChatService')
    def test_generate_narrative_success(self, mock_chat_service, client):
        # Setup
        mock_service_instance = Mock()
        mock_service_instance.generate_narrative.return_value = "Generated narrative"
        mock_chat_service.return_value = mock_service_instance
        
        # Execute
        response = client.post(
            '/chat/narrative',
            data=json.dumps({"text": "Travel notes"}),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['narrative'] == "Generated narrative"

    def test_generate_narrative_no_data(self, client):
        # Execute
        response = client.post('/chat/narrative')
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert "请提供数据" in data['error']

    @patch('weaver.server.routes.chat_route.ChatService')
    def test_get_placeholder_narrative_success(self, mock_chat_service, client):
        # Setup
        mock_service_instance = Mock()
        mock_service_instance.get_placeholder_text.return_value = "Placeholder text"
        mock_chat_service.return_value = mock_service_instance
        
        # Execute
        response = client.get('/chat/placeholder')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['narrative'] == "Placeholder text"

    @patch('weaver.server.routes.chat_route.ChatService')
    def test_chat_with_memory_exception(self, mock_chat_service, client):
        # Setup
        mock_chat_service.side_effect = Exception("Service error")
        
        # Execute
        response = client.post(
            '/memories/mem123/chat',
            data=json.dumps({"message": "Hello"}),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert "对话失败" in data['error']
