import json
from typing import Optional
from uuid import uuid4

from chat2graph.core.service.graph_db_service import GraphDbService  # Added import
from chat2graph.core.toolkit.tool import Tool


class GraphSchemaReader(Tool):
    """Tool for reading the schema of the graph database."""

    def __init__(self, id: Optional[str] = None):
        super().__init__(
            id=id or str(uuid4()),
            name=self.read_graph_schema.__name__,
            description=self.read_graph_schema.__doc__ or "",
            function=self.read_graph_schema,
        )

    async def read_graph_schema(self) -> str:
        """Reads and returns the schema of the currently configured graph database.

        The schema typically includes information about node labels, relationship types,
        and their properties.

        Returns:
            str: A string representation (e.g., JSON) of the graph database schema,
                 or an error message if reading fails.
        """
        try:
            graph_db_service: GraphDbService = GraphDbService.instance
            default_db_config = graph_db_service.get_default_graph_db_config()
            # schema_to_graph_dict returns a specific format for GraphMessage.
            # For a more general schema, get_schema_metadata might be more appropriate,
            # or the raw schema_metadata from the config.
            # Let's use schema_metadata for now as it's more direct.
            schema_metadata = graph_db_service.get_schema_metadata(default_db_config)
            if not schema_metadata:  # handle case where it might be None or empty
                schema_metadata = {"nodes": {}, "relationships": {}}  # Default empty schema
            return json.dumps(schema_metadata, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error reading graph schema: {str(e)}"
