from pathlib import Path
from typing import List, Optional

from weaver.util.file import upload_file


def load_data_v1(folder_path_str: Optional[str] = None) -> List[str]:
    """Load data for the first version of the data loader."""

    folder_path = Path(folder_path_str or "asset/text_data_v1")
    file_paths = []

    # Check if directory exists
    if not folder_path.exists():
        print(f"Warning: Directory {folder_path} does not exist")
        return []

    # get all text file paths from the specified folder
    for file_path in folder_path.glob("*.txt"):
        file_paths.append(str(file_path))

    return upload_file(file_paths)
