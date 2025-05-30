from typing import List

from chat2graph.core.service.file_service import FileService
from werkzeug.datastructures import FileStorage


def upload_file(file_paths: List[str]) -> List[str]:
    """Uploads local files to the server.

    Args:
        file_paths (List[str]): The paths to the files to be uploaded.

    Returns:
        List[str]: The IDs of the uploaded files.
    """
    file_service: FileService = FileService.instance
    file_ids = []

    for file_path in file_paths:
        with open(file_path, "rb") as fp:
            file_storage = FileStorage(fp, filename=file_path.split("/")[-1])
            print(f"[log] uploading file: {file_storage.filename}")
            file_id = file_service.upload_or_update_file(file_storage)
            file_ids.append(file_id)

    return file_ids

def get_file_content(file_id: str) -> str:
    """Retrieves the content of a file given its ID.

    Args:
        file_id (str): The ID of the file to retrieve.

    Returns:
        str: The content of the file.
    """
    file_service: FileService = FileService.instance
    return file_service.read_file(file_id)
