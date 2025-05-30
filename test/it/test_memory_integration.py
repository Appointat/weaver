from io import BytesIO

import requests


class TestMemoryIntegration:
    """
    Integration tests for memory endpoints.
    These tests require the Flask app to be running on localhost:5000
    """
    
    BASE_URL = "http://localhost:5000"
    
    def test_create_memory_json_success(self):
        """Test successful memory creation with JSON data"""
        url = f"{self.BASE_URL}/memories"
        
        memory_data = {
            "tripName": "测试旅行",
            "startDate": "2024-01-01",
            "endDate": "2024-01-02",
            "location": "测试地点",
            "notes": "这是一次美好的旅行",
            "music": "测试音乐"
        }
        
        response = requests.post(
            url,
            json=memory_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'memory' in data
        assert data['memory']['tripName'] == "测试旅行"
        assert data['memory']['location'] == "测试地点"
        assert 'id' in data['memory']
        
        # Store memory ID for other tests
        return data['memory']['id']
    
    def test_create_memory_form_data_success(self):
        """Test successful memory creation with form data and files"""
        url = f"{self.BASE_URL}/memories"
        
        form_data = {
            'trip-name': '表单测试旅行',
            'trip-start-date': '2024-02-01',
            'trip-end-date': '2024-02-02',
            'memory-location': '表单测试地点',
            'memory-text': '这是通过表单提交的旅行记录',
            'memory-music': '表单测试音乐'
        }
        
        files = {
            'memory-photos': ('test_photo.jpg', BytesIO(b'fake image data'), 'image/jpeg')
        }
        
        response = requests.post(url, data=form_data, files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'memory' in data
        assert data['memory']['tripName'] == "表单测试旅行"
        assert data['memory']['photosCount'] >= 0
        
        return data['memory']['id']
    
    def test_create_memory_with_notes_file(self):
        """Test memory creation with uploaded notes file"""
        url = f"{self.BASE_URL}/memories"
        
        form_data = {
            'trip-name': '笔记文件测试',
            'trip-start-date': '2024-03-01',
            'trip-end-date': '2024-03-02',
            'memory-location': '笔记测试地点',
            'memory-music': '笔记测试音乐'
        }
        
        files = {
            "memory-notes-file": ("notes.txt", BytesIO("详细的旅行笔记内容".encode()), "text/plain")
        }
        
        response = requests.post(url, data=form_data, files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert '详细的旅行笔记内容' in data['memory']['notes']
    
    def test_create_memory_validation_error(self):
        """Test memory creation with validation errors"""
        url = f"{self.BASE_URL}/memories"
        
        # Missing required fields
        invalid_data = {
            "tripName": "",  # Empty trip name
            "startDate": "invalid-date",  # Invalid date format
            "location": ""  # Empty location
        }
        
        response = requests.post(
            url,
            json=invalid_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_get_memory_success(self):
        """Test successful memory retrieval"""
        # First create a memory
        memory_id = self.test_create_memory_json_success()
        
        # Then retrieve it
        url = f"{self.BASE_URL}/memories/{memory_id}"
        response = requests.get(url)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'memory' in data
        assert data['memory']['id'] == memory_id
        assert data['memory']['tripName'] == "测试旅行"
    
    def test_get_memory_not_found(self):
        """Test getting non-existent memory"""
        url = f"{self.BASE_URL}/memories/non-existent-id"
        response = requests.get(url)
        
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
        assert "记忆未找到" in data['error']
    
    def test_get_memory_album_success(self):
        """Test successful memory album retrieval"""
        # First create a memory with photos
        memory_id = self.test_create_memory_form_data_success()
        
        # Then get its album
        url = f"{self.BASE_URL}/memories/{memory_id}/album"
        response = requests.get(url)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'album' in data
        assert 'items' in data['album']
        assert 'count' in data['album']
        assert isinstance(data['album']['items'], list)
    
    def test_get_memory_album_not_found(self):
        """Test getting album for non-existent memory"""
        url = f"{self.BASE_URL}/memories/non-existent-id/album"
        response = requests.get(url)
        
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
        assert "记忆未找到" in data['error']
    
    def test_create_memory_no_data(self):
        """Test memory creation with no data"""
        url = f"{self.BASE_URL}/memories"
        
        response = requests.post(url)
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert "请提供有效数据" in data['error']
