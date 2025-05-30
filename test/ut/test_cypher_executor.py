import json
from unittest.mock import MagicMock, patch

import pytest

from weaver.tool_resource.cypher_executor import CypherExecutor, serialize_neo4j_value


# Mock Neo4j graph elements for serialization tests
class MockNode:
    def __init__(self, element_id, labels, properties):
        self.element_id = element_id
        self.labels = set(labels)
        self._properties = properties

    def __iter__(self):  # Make it behave like a dict for dict(node)
        return iter(self._properties)

    def __getitem__(self, key):
        return self._properties[key]

    def keys(self):
        return self._properties.keys()

    def items(self):
        return self._properties.items()


class MockRelationship:
    def __init__(self, element_id, type, start_node, end_node, properties):
        self.element_id = element_id
        self.type = type
        self.start_node = start_node
        self.end_node = end_node
        self._properties = properties

    def __iter__(self):
        return iter(self._properties)

    def __getitem__(self, key):
        return self._properties[key]

    def keys(self):
        return self._properties.keys()

    def items(self):
        return self._properties.items()


class MockPath:
    def __init__(self, nodes, relationships):
        self.nodes = nodes
        self.relationships = relationships


@pytest.fixture
def mock_graph_db_service_for_cypher():
    with (
        patch("weaver.tool_resource.cypher_executor.GraphDbService") as mock_service_class,
        patch("weaver.tool_resource.cypher_executor.Node", new=MockNode),
        patch("weaver.tool_resource.cypher_executor.Relationship", new=MockRelationship),
        patch("weaver.tool_resource.cypher_executor.Path", new=MockPath),
    ):
        mock_instance = MagicMock()

        mock_graph_db = MagicMock()
        mock_instance.get_default_graph_db.return_value = mock_graph_db

        mock_session = MagicMock()
        mock_graph_db.conn.session.return_value.__enter__.return_value = mock_session

        mock_result = MagicMock()
        mock_session.run.return_value = mock_result

        mock_service_class.return_value = mock_instance
        yield mock_instance, mock_result


@pytest.mark.asyncio
async def test_cypher_executor_init():
    executor = CypherExecutor(id="test_cypher_id")
    assert executor.id == "test_cypher_id"
    assert executor.name == "execute_cypher_query"
    assert executor.description == CypherExecutor.execute_cypher_query.__doc__
    assert callable(executor.function)


@pytest.mark.asyncio
async def test_execute_cypher_success_with_results(mock_graph_db_service_for_cypher):
    mock_service, mock_db_result = mock_graph_db_service_for_cypher
    executor = CypherExecutor()
    query = "MATCH (n) RETURN n"

    # Mocking record.data()
    mock_record_data = {"n": MockNode("node1", ["TestLabel"], {"name": "Test"})}
    mock_record = MagicMock()
    mock_record.data.return_value = mock_record_data
    mock_db_result.__iter__.return_value = [mock_record]  # Make result iterable

    result_str = await executor.execute_cypher_query(query)
    result_json = json.loads(result_str)

    assert len(result_json) == 1
    assert result_json[0]["n"]["properties"]["name"] == "Test"

    mock_session = mock_service.get_default_graph_db.return_value.conn.session.return_value.__enter__.return_value
    mock_session.run.assert_called_once_with(query)


@pytest.mark.asyncio
async def test_execute_cypher_success_no_results(mock_graph_db_service_for_cypher):
    mock_service, mock_db_result = mock_graph_db_service_for_cypher
    executor = CypherExecutor()
    query = "MATCH (n:NonExistentLabel) RETURN n"

    mock_db_result.__iter__.return_value = []  # No records

    result_str = await executor.execute_cypher_query(query)

    assert "Cypher query executed successfully. No data returned." in result_str
    assert f"Query: {query}" in result_str


@pytest.mark.asyncio
async def test_execute_cypher_db_error(mock_graph_db_service_for_cypher):
    mock_service, mock_db_result = mock_graph_db_service_for_cypher
    executor = CypherExecutor()
    query = "INVALID QUERY"
    error_message = "Invalid Cypher syntax"

    mock_session = mock_service.get_default_graph_db.return_value.conn.session.return_value.__enter__.return_value
    mock_session.run.side_effect = Exception(error_message)

    result_str = await executor.execute_cypher_query(query)

    assert f"Error executing Cypher query: {error_message}" in result_str
    assert f"Query: {query}" in result_str


def test_serialize_neo4j_value():
    # Test with MockNode
    # Patch Node, Relationship, Path as used by serialize_neo4j_value
    # so that isinstance checks work with our Mock objects.
    with (
        patch("weaver.tool_resource.cypher_executor.Node", new=MockNode),
        patch("weaver.tool_resource.cypher_executor.Relationship", new=MockRelationship),
        patch("weaver.tool_resource.cypher_executor.Path", new=MockPath),
    ):
        node = MockNode("node-123", ["Person", "Developer"], {"name": "Alice", "age": 30})
        serialized_node = serialize_neo4j_value(node)
        expected_node = {
            "id": "node-123",
            "labels": [
                "Person",
                "Developer",
            ],  # Order might vary, so convert to set for comparison if needed
            "properties": {"name": "Alice", "age": 30},
        }
        assert serialized_node["id"] == expected_node["id"]
        assert set(serialized_node["labels"]) == set(expected_node["labels"])
        assert serialized_node["properties"] == expected_node["properties"]

        # Test with MockRelationship
        start_node = MockNode("start-node", ["Test"], {"id": "s1"})
        end_node = MockNode("end-node", ["Test"], {"id": "e1"})
        rel = MockRelationship("rel-456", "KNOWS", start_node, end_node, {"since": 2020})
        serialized_rel = serialize_neo4j_value(rel)
        expected_rel = {
            "id": "rel-456",
            "type": "KNOWS",
            "start_node_id": "start-node",
            "end_node_id": "end-node",
            "properties": {"since": 2020},
        }
        assert serialized_rel == expected_rel

        # Test with MockPath
        path_node1 = MockNode("p_node1", ["L1"], {"key": "v1"})
        path_node2 = MockNode("p_node2", ["L2"], {"key": "v2"})
        path_rel = MockRelationship("p_rel1", "CONNECTS", path_node1, path_node2, {"weight": 1.0})
        path = MockPath([path_node1, path_node2], [path_rel])
        serialized_path = serialize_neo4j_value(path)

        assert len(serialized_path["nodes"]) == 2
        assert serialized_path["nodes"][0]["id"] == "p_node1"
        assert len(serialized_path["relationships"]) == 1
        assert serialized_path["relationships"][0]["id"] == "p_rel1"

        # Test with list
        data_list = [node, 123, "test"]
        serialized_list = serialize_neo4j_value(data_list)
        assert serialized_list[0]["id"] == "node-123"
        assert serialized_list[1] == 123
        assert serialized_list[2] == "test"

        # Test with dict
        data_dict = {"a": node, "b": "simple"}
        serialized_dict = serialize_neo4j_value(data_dict)
        assert serialized_dict["a"]["id"] == "node-123"
        assert serialized_dict["b"] == "simple"

        # Test with basic type
        assert serialize_neo4j_value(123) == 123
        assert serialize_neo4j_value("hello") == "hello"
        assert serialize_neo4j_value(None) is None
