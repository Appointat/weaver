
from chat2graph.core.common.system_env import SystemEnv
from chat2graph.core.dal.dao.dao_factory import DaoFactory
from chat2graph.core.dal.database import DbSession
from chat2graph.core.dal.init_db import init_db
from chat2graph.core.model.graph_db_config import GraphDbConfig
from chat2graph.core.service.graph_db_service import GraphDbService
from chat2graph.core.service.service_factory import ServiceFactory


def init_chat2graph():
    """Initialize the service."""
    init_db()

    DaoFactory.initialize(DbSession())
    ServiceFactory.initialize()

    graph_db_service: GraphDbService = GraphDbService.instance
    graph_db_config: GraphDbConfig = GraphDbConfig(
        name="my_db",
        host=SystemEnv.GRAPH_DB_HOST,
        port=SystemEnv.GRAPH_DB_PORT,
        type=SystemEnv.GRAPH_DB_TYPE,
    )
    graph_db_service.create_graph_db(graph_db_config=graph_db_config)


if __name__ == "__main__":
    init_chat2graph()
