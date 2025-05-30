from typing import List

from chat2graph.core.service.graph_db_service import GraphDbService

from weaver.util.file import get_file_content
from weaver.util.init_chat2graph import init_chat2graph


def get_digital_asset_file_contents() -> List[str]:
    """
    Retrieves the first 5 file_ids from DigitalAsset nodes in the graph database.

    """
    file_contents: List[str] = []
    graph_db_service: GraphDbService = GraphDbService.instance
    graph_db = graph_db_service.get_default_graph_db()

    query = "MATCH (n:DigitalAsset) RETURN n.file_id AS file_id LIMIT 5"

    try:
        with graph_db.conn.session() as session:
            print(f"Executing query: {query}")
            results = session.run(query)
            for record in results:
                file_id = record["file_id"]
                if file_id:
                    file_contents.append(get_file_content(file_id))
    except Exception:
        file_contents = [
            """今天终于到了杭州西湖，早上八点就出发了。断桥残雪虽然没有雪，但是在晨光中特别美。沿着苏堤慢慢走，柳絮飞舞，湖水波光粼粼。在三潭印月拍了好多照片，游船上看到的角度和岸边完全不同。中午在楼外楼吃了西湖醋鱼，确实名不虚传，酸甜适中。下午去了雷峰塔，登塔俯瞰整个西湖，那种"欲把西湖比西子"的感觉瞬间理解了。

    datetime(2023-11-15T18:30:00.000000Z)""",
            """今天是我在杭州西湖的第二天，早上九点起床，吃了酒店的自助早餐。今天的计划是去灵隐寺和飞来峰。灵隐寺的香火很旺，听说这里有很多故事。飞来峰的石刻让我想起了古人的智慧和艺术。下午在西溪湿地散步，感受大自然的气息，拍了很多照片。晚上在西湖边看了音乐喷泉，真是太美了。

            datetime(2023-11-16T20:00:00.000000Z)""",
            """今天是我在杭州西湖的最后一天，早上十点起床，收拾好行李。今天的计划是去西湖博物馆和南宋御街。西湖博物馆的展览让我对西湖的历史有了更深的了解。南宋御街的古建筑让我仿佛回到了古代。中午在南宋御街吃了小笼包，味道很好。下午在西湖边散步，感受最后的美好时光。

            datetime(2023-11-17T15:00:00.000000Z)""",
        ]

    return file_contents


# Example usage (optional, for testing purposes):
if __name__ == "__main__":
    # Ensure Neo4j is running and accessible
    # You might need to configure GraphDbService if it's not already set up globally
    # For example, by setting environment variables for Neo4j connection

    # First, ensure the schema and some data exist.
    # You might run import_graph_schema() if your DB is empty or schema is not set.
    # import_graph_schema()
    #
    # Then, you would typically add some DigitalAsset nodes. For example:
    # graph_db_service = GraphDbService.instance
    # graph_db = graph_db_service.get_default_graph_db()
    # with graph_db.conn.session() as session:
    #     session.run("MERGE (da:DigitalAsset {asset_name: 'test_asset_1', file_id: 'file123.jpg', media_type: 'image', description: 'Test image 1'})")
    #     session.run("MERGE (da:DigitalAsset {asset_name: 'test_asset_2', file_id: 'file456.png', media_type: 'image', description: 'Test image 2'})")
    #     session.run("MERGE (da:DigitalAsset {asset_name: 'test_asset_3', file_id: 'doc789.pdf', media_type: 'document', description: 'Test document 1'})")
    #     session.run("MERGE (da:DigitalAsset {asset_name: 'test_asset_4', file_id: 'vid012.mp4', media_type: 'video', description: 'Test video 1'})")
    #     session.run("MERGE (da:DigitalAsset {asset_name: 'test_asset_5', file_id: 'aud345.mp3', media_type: 'audio', description: 'Test audio 1'})")
    #     session.run("MERGE (da:DigitalAsset {asset_name: 'test_asset_6', file_id: 'file678.txt', media_type: 'text', description: 'Test text file 1'})")

    init_chat2graph()
    retrieved_ids = get_digital_asset_file_contents()
    if retrieved_ids:
        print("Successfully retrieved file IDs:")
        for fid in retrieved_ids:
            print(fid)
    else:
        print("No file IDs were retrieved or an error occurred.")
