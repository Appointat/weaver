import logging

from flask import Blueprint, jsonify, request

from weaver.server.utils.file_handler import allowed_file, save_uploaded_file

logger = logging.getLogger(__name__)
file_bp = Blueprint("file", __name__)


@file_bp.route("/files/upload", methods=["POST"])
def upload_files():
    """文件上传接口

    uploaded_file = {
            "filename": file.filename,
            "file_id": file_id,
    }
    """
    try:
        if "files" not in request.files:
            return jsonify({"success": False, "error": "没有文件被上传"}), 400

        files = request.files.getlist("files")
        if not files or all(f.filename == "" for f in files):
            return jsonify({"success": False, "error": "没有选择文件"}), 400

        uploaded_files = []

        for file in files:
            if file and file.filename and allowed_file(file.filename):
                try:
                    file_info = save_uploaded_file(file)
                    uploaded_files.append(file_info)
                except Exception as e:
                    logger.error(f"Error saving file {file.filename}: {e}")
                    continue

        if not uploaded_files:
            return jsonify({"success": False, "error": "没有有效文件被上传"}), 400

        # 提取file_ids
        file_ids = [file_info["file_id"] for file_info in uploaded_files]

        return jsonify({"success": True, "file_ids": file_ids, "count": len(file_ids)})

    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        return jsonify({"success": False, "error": f"文件上传失败: {str(e)}"}), 500
