import json
import traceback  # Added for error reporting
from typing import Any, Optional
from uuid import uuid4

from chat2graph.core.service.graph_db_service import GraphDbService  # Added import
from chat2graph.core.toolkit.tool import Tool
from neo4j.graph import Node, Path, Relationship  # For result processing


def serialize_neo4j_value(value: Any) -> Any:
    """Recursively serialize Neo4j specific types to JSON-compatible format."""
    if isinstance(value, Node):
        return {"id": value.element_id, "labels": list(value.labels), "properties": dict(value)}
    elif isinstance(value, Relationship):
        return {
            "id": value.element_id,
            "type": value.type,
            "start_node_id": value.start_node.element_id if value.start_node else None,
            "end_node_id": value.end_node.element_id if value.end_node else None,
            "properties": dict(value),
        }
    elif isinstance(value, Path):
        return {
            "nodes": [serialize_neo4j_value(n) for n in value.nodes],
            "relationships": [serialize_neo4j_value(r) for r in value.relationships],
        }
    elif isinstance(value, list):
        return [serialize_neo4j_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: serialize_neo4j_value(v) for k, v in value.items()}
    return value


class CypherExecutor(Tool):
    """Tool for executing Cypher queries against the graph database."""

    def __init__(self, id: Optional[str] = None):
        super().__init__(
            id=id or str(uuid4()),
            name=self.execute_cypher_query.__name__,
            description=self.execute_cypher_query.__doc__ or "",
            function=self.execute_cypher_query,
        )
        self._graph_db_service = GraphDbService()  # Initialize service

    async def execute_cypher_query(self, cypher_query: str) -> str:
        """Executes a given Cypher query against the graph database and returns the results. The version of the
        Neo4j driver used is 5.0.0 +.

        Args:
            cypher_query (str): The Cypher statement to execute.

        Returns:
            str: A string representation (json) of the query results, or an error/success message.
        """
        try:
            graph_db = self._graph_db_service.get_default_graph_db()
            # Assuming graph_db.conn is a Neo4j Driver instance
            with graph_db.conn.session() as session:
                result = session.run(cypher_query)
                records = [record.data() for record in result]  # Get data from records

                # Serialize Neo4j specific types in records for JSON compatibility
                serialized_records = [serialize_neo4j_value(record) for record in records]

            if not serialized_records:
                return f"Cypher query executed successfully. No data returned.\nQuery: {cypher_query}\n"
            return json.dumps(serialized_records, indent=2, ensure_ascii=False)
        except Exception as e:
            tb_str = traceback.format_exc()
            error_message = (
                f"Error executing Cypher query: {str(e)}\n"
                f"Query: {cypher_query}\n"
                f"Traceback:\n{tb_str}"
            )
            print(error_message)  # Log for server-side debugging
            return error_message
