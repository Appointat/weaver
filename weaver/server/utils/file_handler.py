from typing import Any, Dict, List

from chat2graph.core.service.file_service import FileService
from werkzeug.datastructures import FileStorage

ALLOWED_EXTENSIONS = {
    "txt",
    "md",  # 文档
    "jpg",
    "jpeg",
    "png",
    "gif",
    "bmp",  # 图片
    # 'mp4', 'avi', 'mov', 'wmv', 'flv',   # 视频
    # 'mp3', 'wav', 'flac', 'aac'          # 音频
}


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否被允许"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file: FileStorage) -> Dict[str, Any]:
    """保存上传的文件并返回文件信息"""
    if not file or not file.filename:
        raise ValueError("无效的文件")

    if not allowed_file(file.filename):
        raise ValueError(f"不支持的文件类型: {file.filename}")

    # 保存文件
    file_service: FileService = FileService.instance
    file_id = file_service.upload_or_update_file(file)

    return {
        "filename": file.filename,
        "file_id": file_id,
    }

def handle_uploaded_files(files: List) -> List[Dict[str, Any]]:
    """处理多个上传文件"""
    file_info_list = []
    
    for file in files:
        if file and file.filename:
            try:
                file_info = save_uploaded_file(file)
                file_info_list.append(file_info)
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")
                continue
    
    return file_info_list

def get_file_type(extension: str) -> str:
    """根据文件扩展名获取文件类型"""
    image_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
    video_exts = {'mp4', 'avi', 'mov', 'wmv', 'flv'}
    audio_exts = {'mp3', 'wav', 'flac', 'aac'}
    doc_exts = {'txt', 'md', 'pdf', 'doc', 'docx'}
    
    if extension in image_exts:
        return 'image'
    elif extension in video_exts:
        return 'video'
    elif extension in audio_exts:
        return 'audio'
    elif extension in doc_exts:
        return 'document'
    else:
        return 'unknown'
