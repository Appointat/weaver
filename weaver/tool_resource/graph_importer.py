import json
import traceback
from typing import Any, Dict, Optional
from uuid import uuid4

from chat2graph.core.service.graph_db_service import GraphDbService
from chat2graph.core.toolkit.tool import Tool

from weaver.util.embedding import get_embed_vec


class GraphImporter(Tool):
    """Tool for importing graph data (nodes and relationships) into Neo4j database."""

    def __init__(self, id: Optional[str] = None):
        super().__init__(
            id=id or str(uuid4()),
            name=self.import_graph.__name__,
            description=self.import_graph.__doc__ or "",
            function=self.import_graph,
        )
        self._graph_db_service = GraphDbService()

    async def import_graph(self, graph_data: Dict[str, Any]) -> str:
        """Imports graph data (nodes and relationships) into the Neo4j database.

        This method accepts a dictionary containing nodes and relationships data, then
        generates and executes appropriate Cypher CREATE/MERGE statements to import
        the data into the graph database.

        Args:
            graph_data (Dict[str, Any]): A dictionary containing the graph data to import.
                The expected format follows the schema structure:

                {
                    "nodes": {
                        "NodeLabel": [
                            {
                                "primary_key_name": "unique_identifier",
                                "property1": "value1",
                                "property2": "value2",
                                "embed": [0.1, 0.2, 0.3, ...],  # Optional embedding vector
                                ...
                            },
                            ...
                        ]
                    },
                    "relationships": {
                        "RELATIONSHIP_TYPE": [
                            {
                                "id": "relationship_id",
                                "source_node": {
                                    "label": "SourceLabel",
                                    "key": "source_primary_key_value"
                                },
                                "target_node": {
                                    "label": "TargetLabel",
                                    "key": "target_primary_key_value"
                                },
                                "properties": {
                                    "property1": "value1",
                                    ...
                                }
                            },
                            ...
                        ]
                    }
                }

        Returns:
            str: Success message with detailed import statistics, including lists of
                 imported nodes and relationships, or error message if import fails.

        Examples:
            Simple node import:
            <function_call>
            {
                "name": "import_graph",
                "call_objective": "Import experiential scene and observation nodes into Neo4j database",
                "args": {
                    "graph_data": {
                        "nodes": {
                            "ExperientialScene": [
                                {
                                    "scene_name": "kyoto_temple_visit",
                                    "description": "Peaceful morning at Kinkaku-ji temple",
                                    "timestamp": "2023-11-15T08:30:00Z",
                                    "location_text": "Kyoto, Japan",
                                    "embed": [0.1, 0.2, 0.3]
                                }
                            ],
                            "FocalObservation": [
                                {
                                    "observation_name": "golden_reflection",
                                    "observed_element": "Temple's golden reflection in pond",
                                    "significance": "Symbol of tranquility",
                                    "timestamp": "2023-11-15T08:35:00Z"
                                }
                            ]
                        }
                    }
                }
            }
            </function_call>


            Complete graph with relationships:
            <function_call>
            {
                "name": "import_graph",
                "call_objective": "Import scene, emotion nodes and their relationship into Neo4j database",
                "args": {
                    "graph_data": {
                        "nodes": {
                            "ExperientialScene": [
                                {
                                    "scene_name": "beach_sunset",
                                    "description": "Serene sunset at the beach",
                                    "timestamp": "2023-11-15T18:00:00Z"
                                }
                            ],
                            "AffectiveResonance": [
                                {
                                    "resonance_name": "peaceful_moment",
                                    "emotion_label": "Peaceful",
                                    "trigger_description": "Watching the sunset",
                                    "timestamp": "2023-11-15T18:15:00Z"
                                }
                            ]
                        },
                        "relationships": {
                            "TRIGGERED_BY": [
                                {
                                    "id": "emotion_from_sunset",
                                    "source_node": {
                                        "label": "AffectiveResonance",
                                        "key": "peaceful_moment"
                                    },
                                    "target_node": {
                                        "label": "ExperientialScene",
                                        "key": "beach_sunset"
                                    },
                                    "properties": {}
                                }
                            ]
                        }
                    }
                }
            }
            </function_call>

            Digital asset import:
            <function_call>
            {
                "name": "import_graph",
                "call_objective": "Import digital asset and city nodes into Neo4j database",
                "args": {
                    "graph_data": {
                        "nodes": {
                            "DigitalAsset": [
                                {
                                    "asset_name": "81679340_647f_402b_88f5_25142d8fd0d8",
                                    "description": "新疆喀纳斯游记",
                                    "file_id": "81679340-647f-402b-88f5-25142d8fd0d8",
                                    "media_type": "text",
                                    "timestamp": "2025-05-23T09:22:20.829366Z"
                                }
                            ],
                            "City": [
                                {
                                    "city_name": "kanas_scenic_area",
                                    "description": "Beautiful natural landscape in Xinjiang",
                                    "location": "Xinjiang, China"
                                }
                            ]
                        }
                    }
                }
            }
            </function_call>


        Note:
            - Uses MERGE statements to avoid duplicates based on primary keys
            - Embedding vectors (embed property) are stored as LIST OF FLOAT in Neo4j
            - All timestamps should be in ISO 8601 format for Neo4j DATETIME compatibility
            - Primary keys must be in English only and follow naming conventions
            - Relationships are created only if both source and target nodes exist
        """
        try:
            created_nodes = 0
            created_relationships = 0
            imported_nodes = []
            imported_relationships = []

            graph_db = self._graph_db_service.get_default_graph_db()

            with graph_db.conn.session() as session:
                # Import nodes first
                nodes_data = graph_data.get("nodes", {})
                for node_label, node_list in nodes_data.items():
                    for node in node_list:
                        primary_key = self._get_primary_key_for_label(node_label)
                        primary_value = node.get(primary_key)

                        # Handle missing primary key
                        if not primary_value:
                            for fallback_key in [
                                "id",
                                "name",
                                list(node.keys())[0] if node else None,
                            ]:
                                if fallback_key and fallback_key in node and node[fallback_key]:
                                    primary_key = fallback_key
                                    primary_value = node[fallback_key]
                                    break
                            if not primary_value:
                                primary_key = "id"
                                primary_value = str(uuid4())
                                node[primary_key] = primary_value

                        cypher = self._generate_node_cypher(node_label, node)
                        session.run(cypher, node)
                        created_nodes += 1
                        imported_nodes.append(f"{node_label}({primary_key}: {primary_value})")

                # Import relationships after nodes
                relationships_data = graph_data.get("relationships", {})
                for rel_type, rel_list in relationships_data.items():
                    for relationship in rel_list:
                        cypher = self._generate_relationship_cypher(rel_type, relationship)
                        if cypher:  # Only execute if cypher was generated successfully
                            session.run(cypher, relationship)
                            created_relationships += 1

                            source = relationship.get("source_node", {})
                            target = relationship.get("target_node", {})
                            source_label = source.get("label", "Unknown")
                            source_key = source.get("key", "Unknown")
                            target_label = target.get("label", "Unknown")
                            target_key = target.get("key", "Unknown")

                            imported_relationships.append(
                                f"{source_label}({source_key})-[:{rel_type}]->{target_label}({target_key})"
                            )

            # Build detailed response
            result_parts = [
                "Graph data imported successfully!",
                f"Created/Updated {created_nodes} nodes",
                f"Created {created_relationships} relationships",
                "",
            ]

            if imported_nodes:
                result_parts.append("Imported Nodes:")
                for node in imported_nodes:
                    result_parts.append(f"  - {node}")
                result_parts.append("")

            if imported_relationships:
                result_parts.append("Imported Relationships:")
                for rel in imported_relationships:
                    result_parts.append(f"  - {rel}")

            return "\n".join(result_parts)

        except Exception as e:
            tb_str = traceback.format_exc()
            error_message = (
                f"Error importing graph data: {str(e)}\n"
                f"Data: {json.dumps(graph_data, indent=2, ensure_ascii=False)}\n"
                f"Traceback:\n{tb_str}"
            )
            print(error_message)
            return error_message

    def _generate_node_cypher(self, label: str, node_data: Dict[str, Any]) -> str:
        """Generate MERGE cypher for a node."""
        # Get primary key for the label
        primary_key = self._get_primary_key_for_label(label)
        primary_value = node_data.get(primary_key)

        # If primary key is missing, try to find any unique identifier or use a generated one
        if not primary_value:
            # Try common fallback keys
            for fallback_key in ["id", "name", list(node_data.keys())[0] if node_data else None]:
                if fallback_key and fallback_key in node_data and node_data[fallback_key]:
                    primary_key = fallback_key
                    primary_value = node_data[fallback_key]
                    break
            
            # If still no primary key, generate one
            if not primary_value:
                primary_key = "id"
                primary_value = str(uuid4())
                node_data[primary_key] = primary_value

        # Generate embedding vector for the node
        # Use description if available, otherwise use the primary value as text
        text_for_embedding = node_data.get("description") or str(primary_value)
        embed_vector = get_embed_vec(text_for_embedding)
        if embed_vector:
            node_data["embed"] = embed_vector

        # Build property string - always SET all properties to overwrite existing ones
        property_assignments = []
        for key, value in node_data.items():
            property_assignments.append(f"n.{key} = ${key}")

        properties_str = ", ".join(property_assignments)

        return f"MERGE (n:{label} {{{primary_key}: ${primary_key}}}) SET {properties_str}"

    def _generate_relationship_cypher(
        self, rel_type: str, rel_data: Dict[str, Any]
    ) -> Optional[str]:
        """Generate CREATE cypher for a relationship."""
        source = rel_data.get("source_node", {})
        target = rel_data.get("target_node", {})
        properties = rel_data.get("properties", {})

        if not source or not target:
            print(f"Warning: Missing source or target node data for relationship {rel_type}")
            return None

        source_label = source.get("label")
        source_key = source.get("key")
        target_label = target.get("label")
        target_key = target.get("key")

        if not all([source_label, source_key, target_label, target_key]):
            print(f"Warning: Incomplete node reference data for relationship {rel_type}")
            return None

        # Get primary keys for source and target labels
        source_primary_key = self._get_primary_key_for_label(source_label)
        target_primary_key = self._get_primary_key_for_label(target_label)

        # Build relationship properties
        rel_props = ""
        if properties or "id" in rel_data:
            prop_items = []
            if "id" in rel_data:
                prop_items.append(f"id: '{rel_data['id']}'")
            for key, value in properties.items():
                if isinstance(value, str):
                    prop_items.append(f"{key}: '{value}'")
                else:
                    prop_items.append(f"{key}: {value}")
            if prop_items:
                rel_props = f" {{{', '.join(prop_items)}}}"

        return (
            f"MATCH (s:{source_label} {{{source_primary_key}: '{source_key}'}}) "
            f"MATCH (t:{target_label} {{{target_primary_key}: '{target_key}'}}) "
            f"CREATE (s)-[r:{rel_type}{rel_props}]->(t)"
        )

    def _get_primary_key_for_label(self, label: str) -> str:
        """Get the primary key name for a given node label."""
        # Map labels to their primary keys based on schema
        primary_key_mapping = {
            "ExperientialScene": "scene_name",
            "FocalObservation": "observation_name",
            "AffectiveResonance": "resonance_name",
            "NarrativeAnchor": "anchor_name",
            "InteractionPoint": "interaction_name",
            "DigitalAsset": "asset_name",
        }
        return primary_key_mapping.get(label, "id")
