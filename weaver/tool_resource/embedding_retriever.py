import json
from typing import Any, Dict, List, Optional
from uuid import uuid4

from chat2graph.core.dal.dao.dao_factory import DaoFactory
from chat2graph.core.dal.database import DbSession
from chat2graph.core.service.graph_db_service import GraphDbService
from chat2graph.core.service.service_factory import ServiceFactory
from chat2graph.core.toolkit.tool import Tool

from weaver.util.embedding import get_embed_vec


class EmbeddingRetriever(Tool):
    """Tool for computing embeddings and retrieving similar nodes from the graph database."""

    def __init__(self, id: Optional[str] = None):
        super().__init__(
            id=id or str(uuid4()),
            name=self.find_similar_nodes.__name__,
            description=self.find_similar_nodes.__doc__ or "",
            function=self.find_similar_nodes,
        )
        self._graph_db_service = GraphDbService()

    async def find_similar_nodes(
        self, text_content: str, top_k: int = 5, similarity_threshold: float = 0.7
    ) -> str:
        """Computes embedding for text and finds similar nodes in the graph database using vector similarity.

        Args:
            text_content (str): The text content to embed and search for similar nodes.
                               Example: '京都的岚山竹林'
            top_k (int): Number of top similar nodes to return. Default: 5
            similarity_threshold (float): Minimum similarity score (0-1). Default: 0.7

        Returns:
            str: JSON string containing similar nodes and their connections,
                 or an error message if computation/search fails.
        """
        try:
            # Step 1: Compute embedding for input text
            embedding_vector = get_embed_vec(text_content)

            if embedding_vector is None:
                return f"Failed to compute embedding for text: {text_content}"

            # Step 2: Perform vector similarity search in Neo4j
            similar_nodes = await self._search_similar_nodes(
                embedding_vector, top_k, similarity_threshold
            )

            if not similar_nodes:
                return f"No similar nodes found for text: '{text_content}' with threshold {similarity_threshold}"

            # Step 3: Get graph structure around similar nodes
            graph_data = await self._get_graph_around_nodes(similar_nodes)

            result = {
                "query_text": text_content,
                "query_embedding_dimension": len(embedding_vector),
                "similar_nodes": similar_nodes,
                "graph_structure": graph_data,
                "search_params": {"top_k": top_k, "similarity_threshold": similarity_threshold},
            }

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            error_message = f"Error finding similar nodes for text '{text_content}': {str(e)}"
            print(error_message)
            return error_message

    async def _search_similar_nodes(
        self, embedding_vector: List[float], top_k: int, similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """Search for nodes with similar embeddings using vector index."""
        # Use vector similarity search with cosine similarity
        cypher_query = """
        CALL db.index.vector.queryNodes('*_embed_vector_index', $top_k, $embedding_vector)
        YIELD node, score
        WHERE score >= $similarity_threshold
        RETURN 
            labels(node)[0] as node_type,
            properties(node) as node_properties,
            score as similarity_score
        ORDER BY score DESC
        """

        params = {
            "embedding_vector": embedding_vector,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
        }

        try:
            graph_db = self._graph_db_service.get_default_graph_db()
            with graph_db.conn.session() as session:
                result = session.run(cypher_query, parameters=params)

                similar_nodes = []
                for record in result:
                    properties = dict(record["node_properties"])
                    # Filter out embed vector from properties
                    properties.pop("embed", None)

                    node_data = {
                        "node_type": record["node_type"],
                        "properties": properties,
                        "similarity_score": record["similarity_score"],
                    }
                    similar_nodes.append(node_data)

                return similar_nodes

        except Exception as e:
            print(f"Error in vector similarity search: {e}")
            # Fallback to property-based search if vector search fails
            return await self._fallback_property_search(embedding_vector, top_k)

    async def _fallback_property_search(
        self, embedding_vector: List[float], top_k: int
    ) -> List[Dict[str, Any]]:
        """Fallback search using node properties when vector search is unavailable."""
        cypher_query = """
        MATCH (n)
        WHERE n.embed IS NOT NULL
        RETURN 
            labels(n)[0] as node_type,
            properties(n) as node_properties,
            0.5 as similarity_score
        LIMIT $top_k
        """

        params = {"top_k": top_k}

        try:
            graph_db = self._graph_db_service.get_default_graph_db()
            with graph_db.conn.session() as session:
                result = session.run(cypher_query, parameters=params)

                nodes = []
                for record in result:
                    properties = dict(record["node_properties"])
                    # Filter out embed vector from properties
                    properties.pop("embed", None)

                    node_data = {
                        "node_type": record["node_type"],
                        "properties": properties,
                        "similarity_score": record["similarity_score"],
                    }
                    nodes.append(node_data)

                return nodes

        except Exception as e:
            print(f"Error in fallback search: {e}")
            return []

    async def _get_graph_around_nodes(self, similar_nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get the graph structure (nodes and relationships) around the similar nodes."""
        if not similar_nodes:
            return {"nodes": [], "relationships": []}

        # Extract node identifiers for graph expansion
        node_conditions = []
        params = {}

        for i, node_data in enumerate(similar_nodes):
            node_type = node_data["node_type"]
            properties = node_data["properties"]

            # Use the primary key to identify nodes
            if node_type == "ExperientialScene" and "scene_name" in properties:
                node_conditions.append(f"(n.scene_name = $scene_name_{i})")
                params[f"scene_name_{i}"] = properties["scene_name"]
            elif node_type == "FocalObservation" and "observation_name" in properties:
                node_conditions.append(f"(n.observation_name = $observation_name_{i})")
                params[f"observation_name_{i}"] = properties["observation_name"]
            elif node_type == "AffectiveResonance" and "resonance_name" in properties:
                node_conditions.append(f"(n.resonance_name = $resonance_name_{i})")
                params[f"resonance_name_{i}"] = properties["resonance_name"]
            elif node_type == "NarrativeAnchor" and "anchor_name" in properties:
                node_conditions.append(f"(n.anchor_name = $anchor_name_{i})")
                params[f"anchor_name_{i}"] = properties["anchor_name"]
            elif node_type == "InteractionPoint" and "interaction_name" in properties:
                node_conditions.append(f"(n.interaction_name = $interaction_name_{i})")
                params[f"interaction_name_{i}"] = properties["interaction_name"]

        if not node_conditions:
            return {"nodes": [], "relationships": []}

        # Get 1-hop neighborhood around similar nodes
        cypher_query = f"""
        MATCH (n)
        WHERE {" OR ".join(node_conditions)}
        OPTIONAL MATCH (n)-[r]-(connected)
        RETURN 
            collect(DISTINCT {{
                id: coalesce(n.scene_name, n.observation_name, n.resonance_name, n.anchor_name, n.interaction_name, n.asset_name, n.city_name, n.province_name, n.season_name),
                labels: labels(n),
                properties: properties(n)
            }}) as nodes,
            collect(DISTINCT {{
                id: r.id,
                type: type(r),
                source: coalesce(startNode(r).scene_name, startNode(r).observation_name, startNode(r).resonance_name, startNode(r).anchor_name, startNode(r).interaction_name, startNode(r).asset_name, startNode(r).city_name, startNode(r).province_name, startNode(r).season_name),
                target: coalesce(endNode(r).scene_name, endNode(r).observation_name, endNode(r).resonance_name, endNode(r).anchor_name, endNode(r).interaction_name, endNode(r).asset_name, endNode(r).city_name, endNode(r).province_name, endNode(r).season_name),
                properties: properties(r)
            }}) as relationships
        """

        try:
            graph_db = self._graph_db_service.get_default_graph_db()
            with graph_db.conn.session() as session:
                result = session.run(cypher_query, parameters=params)
                record = result.single()

                if record:
                    # Filter out embed vectors from node properties
                    filtered_nodes = []
                    for node in record["nodes"]:
                        node_dict = dict(node or {})
                        node_dict.pop("embed", None)
                        if "properties" in node_dict:
                            node_dict["properties"].pop("embed", None)
                        filtered_nodes.append(node_dict)

                    return {
                        "nodes": filtered_nodes,
                        "relationships": [
                            dict(rel) for rel in record["relationships"] if rel["id"] is not None
                        ],
                    }
                else:
                    return {"nodes": [], "relationships": []}

        except Exception as e:
            print(f"Error getting graph structure: {e}")
            return {"nodes": [], "relationships": []}


DaoFactory.initialize(DbSession())
ServiceFactory.initialize()


async def main():
    """Test function for EmbeddingRetriever with example input."""
    # Create an instance of the tool

    retriever = EmbeddingRetriever()

    test_input = "杭州西湖"
    print(f"Testing EmbeddingRetriever with input: '{test_input}'")
    print("=" * 50)

    try:
        # Call the find_similar_nodes function
        result = await retriever.find_similar_nodes(
            text_content=test_input,
            top_k=3,  # Get top 3 similar nodes
            similarity_threshold=0.6,  # Lower threshold for testing
        )

        print("Result:")
        print(result)

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import asyncio

    print("Starting EmbeddingRetriever test...")
    asyncio.run(main())
