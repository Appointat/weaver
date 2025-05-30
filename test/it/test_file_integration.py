from io import BytesIO

import requests


class TestFileIntegration:
    """
    Integration tests for file upload endpoints.
    These tests require the Flask app to be running on localhost:5000
    """
    
    BASE_URL = "http://localhost:5000"
    
    def test_upload_single_file_success(self):
        """Test successful single file upload"""
        url = f"{self.BASE_URL}/files/upload"
        
        # Create a fake image file
        files = {
            'files': ('test_image.jpg', BytesIO(b'fake image data'), 'image/jpeg')
        }
        
        response = requests.post(url, files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['count'] == 1
        assert len(data['file_ids']) == 1
        assert isinstance(data['file_ids'][0], str)
    
    def test_upload_multiple_files_success(self):
        """Test successful multiple files upload"""
        url = f"{self.BASE_URL}/files/upload"
        
        # Create multiple fake files
        files = [
            ('files', ('image1.jpg', BytesIO(b'fake image data 1'), 'image/jpeg')),
            ('files', ('image2.png', BytesIO(b'fake image data 2'), 'image/png')),
            ('files', ('video.mp4', BytesIO(b'fake video data'), 'video/mp4'))
        ]
        
        response = requests.post(url, files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['count'] == 3
        assert len(data['file_ids']) == 3
    
    def test_upload_no_files(self):
        """Test upload with no files"""
        url = f"{self.BASE_URL}/files/upload"
        
        response = requests.post(url, data={})
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert "没有文件被上传" in data['error']
    
    def test_upload_empty_filename(self):
        """Test upload with empty filename"""
        url = f"{self.BASE_URL}/files/upload"
        
        files = {
            'files': ('', BytesIO(b''), 'application/octet-stream')
        }
        
        response = requests.post(url, files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert "没有选择文件" in data['error']
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        url = f"{self.BASE_URL}/files/upload"
        
        files = {
            'files': ('malware.exe', BytesIO(b'fake executable'), 'application/x-executable')
        }
        
        response = requests.post(url, files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert "没有有效文件被上传" in data['error']
    
    def test_upload_mixed_valid_invalid_files(self):
        """Test upload with mix of valid and invalid files"""
        url = f"{self.BASE_URL}/files/upload"
        
        files = [
            ('files', ('valid_image.jpg', BytesIO(b'fake image data'), 'image/jpeg')),
            ('files', ('invalid.exe', BytesIO(b'fake executable'), 'application/x-executable')),
            ('files', ('valid_video.mp4', BytesIO(b'fake video data'), 'video/mp4'))
        ]
        
        response = requests.post(url, files=files)
        
        # Should succeed with only valid files
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['count'] == 2  # Only valid files processed
        assert len(data['file_ids']) == 2
