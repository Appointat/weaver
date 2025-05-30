from datetime import datetime
from typing import Any, Dict, Optional


def validate_memory_data(data: Dict[str, Any]) -> Optional[str]:
    """验证记忆创建数据 - 对应HTML页面的表单验证"""
    required_fields = {
        'tripName': '旅程名称',
        'startDate': '开始日期', 
        'location': '地点',
        'notes': '笔记'
    }
    
    # 检查必填字段
    for field, field_name in required_fields.items():
        if not data.get(field) or not str(data[field]).strip():
            return f'{field_name}不能为空'
    
    # 验证旅程名称长度
    trip_name = data.get('tripName', '').strip()
    if len(trip_name) > 100:
        return '旅程名称不能超过100个字符'
    
    # 验证日期格式
    start_date = data.get('startDate', '').strip()
    end_date = data.get('endDate', '').strip()
    
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if end_dt < start_dt:
                return '结束日期不能早于开始日期'
    except ValueError:
        return '日期格式不正确，请使用YYYY-MM-DD格式'
    
    # 验证地点
    location = data.get('location', '').strip()
    if len(location) > 200:
        return '地点信息不能超过200个字符'
    
    # 验证笔记内容
    notes = data.get('notes', '').strip()
    if len(notes) < 10:
        return '笔记内容至少需要10个字符'
    if len(notes) > 5000:
        return '笔记内容不能超过5000个字符'
    
    # 验证音乐信息（可选）
    music = data.get('music', '').strip()
    if music and len(music) > 200:
        return '音乐信息不能超过200个字符'
    
    return None

def validate_chat_message(data: Dict[str, Any]) -> Optional[str]:
    """验证聊天消息数据"""
    if not data:
        return '请提供消息数据'
    
    # 检查message字段
    if 'message' not in data:
        return '消息字段不能为空'
    
    message = data['message']
    if not message or not str(message).strip():
        return '聊天消息不能为空'
    
    message = str(message).strip()
    if len(message) < 1:
        return '聊天消息不能为空'
    
    if len(message) > 1000:
        return '聊天消息过长，请控制在1000字符以内'
    
    # 检查是否包含不当内容（简单过滤）
    forbidden_words = ['spam', 'advertisement']  # 可以扩展
    message_lower = message.lower()
    for word in forbidden_words:
        if word in message_lower:
            return '消息包含不当内容'
    
    return None

def validate_file_upload(files: list) -> Optional[str]:
    """验证文件上传"""
    if not files:
        return None  # 文件上传是可选的
    
    max_files = 10
    if len(files) > max_files:
        return f'最多只能上传{max_files}个文件'
    
    max_file_size = 10 * 1024 * 1024  # 10MB
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'txt', 'md', 'pdf'}
    
    for file in files:
        if not file.filename:
            continue
            
        # 检查文件扩展名
        if '.' not in file.filename:
            return f'文件{file.filename}没有扩展名'
        
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return f'不支持的文件类型: {ext}'
        
        # 检查文件大小（如果可能）
        if hasattr(file, 'content_length') and file.content_length:
            if file.content_length > max_file_size:
                return f'文件{file.filename}过大，请上传小于10MB的文件'
    
    return None

def validate_pagination(page: str, limit: str) -> tuple:
    """验证分页参数"""
    try:
        page_int = int(page) if page else 1
        limit_int = int(limit) if limit else 10
        
        if page_int < 1:
            page_int = 1
        if limit_int < 1:
            limit_int = 10
        if limit_int > 100:
            limit_int = 100
            
        return page_int, limit_int
    except ValueError:
        return 1, 10
