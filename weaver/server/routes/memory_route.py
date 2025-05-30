import logging
import random
import time
from typing import Any, Dict

from flask import Blueprint, jsonify, request

from weaver.server.services.memory_service import MemoryService
from weaver.server.utils.file_handler import handle_uploaded_files
from weaver.server.utils.validators import validate_memory_data

logger = logging.getLogger(__name__)
memory_bp = Blueprint('memory', __name__)

@memory_bp.route('/memories', methods=['POST'])
def create_memory():
    """创建新的记忆 - 对应HTML页面的记忆编织功能

    支持的输入数据结构示例:

    1. JSON格式 (Content-Type: application/json):
    {
        "tripName": "京都秋日私语",
        "startDate": "2024-03-15",
        "endDate": "2024-03-20",
        "location": "清水寺, 京都, 日本",
        "notes": "今天在清水寺看到了美丽的樱花，心情格外舒畅...",
        "music": "坂本龙一 - Merry Christmas Mr. Lawrence"
    }

    2. 表单数据格式 (Content-Type: multipart/form-data):
    - trip-name: "京都秋日私语"
    - trip-start-date: "2024-03-15"
    - trip-end-date: "2024-03-20"
    - memory-location: "清水寺, 京都, 日本"
    - memory-text: "今天在清水寺看到了美丽的樱花..."
    - memory-music: "坂本龙一 - Merry Christmas Mr. Lawrence"
    - memory-notes-file: [文件] (可选, .txt/.md格式)
    - memory-photos: [文件数组] (可选, 图片/视频文件)

    返回数据结构:
    {
        "success": true,
        "memory": {
            "id": "uuid-string",
            "tripName": "京都秋日私语",
            "location": "清水寺, 京都, 日本",
            "startDate": "2024-03-15",
            "endDate": "2024-03-20",
            "notes": "用户的旅行笔记内容...",
            "music": "坂本龙一 - Merry Christmas Mr. Lawrence",
            "narrative": "AI生成的回忆叙述...",
            "insights": {
                "themes": ["探索发现", "文化体验"],
                "emotions": ["愉悦", "感动"],
                "recommendation": "建议下次..."
            },
            "tags": ["旅行", "京都", "樱花"],
            "album": {
                "items": [...],
                "count": 3
            },
            "createdAt": "2024-03-15T10:30:00.000Z",
            "photosCount": 2
        }
    }
    """
    try:
        # Handle multipart form data (text + files)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Extract form data
            data: Dict[str, Any] = {
                'tripName': request.form.get('trip-name', '').strip(),
                'startDate': request.form.get('trip-start-date', '').strip(),
                'endDate': request.form.get('trip-end-date', '').strip(),
                'location': request.form.get('memory-location', '').strip(),
                'notes': request.form.get('memory-text', '').strip(),
                'music': request.form.get('memory-music', '').strip()
            }

            # Handle notes file upload
            notes_file = request.files.get('memory-notes-file')
            if notes_file and notes_file.filename:
                try:
                    notes_content = notes_file.read().decode('utf-8')
                    if notes_content.strip():
                        data['notes'] = notes_content
                except Exception as e:
                    logger.warning(f"Failed to read notes file: {e}")

            # Handle photo/video uploads
            photo_files = request.files.getlist('memory-photos')
            
        else:
            # Handle JSON data
            json_data = request.get_json()
            if not json_data:
                return jsonify({'success': False, 'error': '请提供有效数据'}), 400
            
            data = {
                'tripName': json_data.get('tripName', '').strip(),
                'startDate': json_data.get('startDate', '').strip(),
                'endDate': json_data.get('endDate', '').strip(),
                'location': json_data.get('location', '').strip(),
                'notes': json_data.get('notes', '').strip(),
                'music': json_data.get('music', '').strip()
            }
            photo_files = []
        
        # Validate required fields
        validation_error = validate_memory_data(data)
        if validation_error:
            return jsonify({'success': False, 'error': validation_error}), 400
        
        # Process uploaded files
        file_info = handle_uploaded_files(photo_files) if photo_files else []
        data['photosCount'] = len(file_info)
        data['uploadedFiles'] = file_info
        
        # Create memory using service
        memory_service = MemoryService()
        memory = memory_service.create_memory(data)

        return jsonify({
            'success': True,
            'memory': memory
        })

    except Exception as e:
        logger.error(f"Error creating memory: {e}")
        return jsonify({
            'success': False,
            'error': f'创建记忆失败: {str(e)}'
        }), 500


@memory_bp.route("/memories/album", methods=["GET"])
def get_memory_album():
    """获取记忆相册 - 对应HTML页面的多媒体记忆相册功能

    URL参数:
    - memory_id: 记忆的唯一标识符

    返回数据结构:
    {
        "success": true,
        "album": ["文本", "文本", ...],
    }
    """
    try:
        memory_service = MemoryService()
        time.sleep(random.randint(2, 5))  # 模拟处理时间
        album = memory_service.get_memory_album()
        
        if not album:
            return jsonify({
                'success': False,
                'error': '记忆未找到'
            }), 404
        
        return jsonify({
            'success': True,
            'album': album
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"获取相册失败: {str(e)}"}), 500
