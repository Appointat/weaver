import json
from typing import Dict, List, Optional
from uuid import uuid4

from chat2graph.core.service.file_service import FileService
from chat2graph.core.toolkit.tool import Tool

# Assuming a FileService or similar might exist for actual file operations.
# For now, this tool will have a placeholder implementation.


class FileReader(Tool):
    """Tool for reading content from a specified file ID."""

    def __init__(self, id: Optional[str] = None):
        super().__init__(
            id=id or str(uuid4()),
            name=self.read_file_content.__name__,
            description=self.read_file_content.__doc__ or "",
            function=self.read_file_content,
        )

    async def read_file_content(self, file_service: FileService, file_ids: List[str]) -> str:
        """Read the contents of the files specified by the given file IDs.

        Args:
            file_ids (List[str]): The list of unique identifiers for the file to be read.
                             Example: ["document_xyz_123", "document_abc_456"]

        Returns:
            str: A string representation (e.g., JSON) of the file contents,
        """
        results: Dict[str, str] = {}
        for file_id in file_ids:
            results[file_id] = file_service.read_file(file_id=file_id)

        return json.dumps(results, indent=2, ensure_ascii=False)
