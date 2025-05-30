import sys
import time

from chat2graph.core.common.system_env import SystemEnv
from chat2graph.core.service.graph_db_service import GraphDbService
from neo4j import GraphDatabase
import requests

from weaver.util.init_chat2graph import init_chat2graph

init_chat2graph()

def test_http_interface(host=None, port=7474):
    """测试Neo4j HTTP界面是否可访问"""
    if host is None:
        host = SystemEnv.GRAPH_DB_HOST
    try:
        url = f"http://{host}:{port}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ HTTP界面访问成功: {url}")
            return True
        else:
            print(f"❌ HTTP界面访问失败: {url} (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ HTTP界面连接失败: {e}")
        return False


def test_bolt_connection(uri, username="neo4j", password="neo4j"):
    """测试Neo4j Bolt连接"""
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # 验证连接
        with driver.session() as session:
            result = session.run("RETURN 'Hello, Neo4j!' as message")
            record = result.single()
            message = record["message"]
            
        driver.close()
        print(f"✅ Bolt连接成功: {uri}")
        print(f"   返回消息: {message}")
        return True
        
    except Exception as e:
        print(f"❌ Bolt连接失败: {uri}")
        print(f"   错误: {e}")
        return False


def test_database_operations(uri, username="neo4j", password="neo4j"):
    """测试基本数据库操作"""
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            # 创建测试节点
            session.run("CREATE (test:TestNode {name: 'ConnectionTest', timestamp: $timestamp})", 
                       timestamp=int(time.time()))
            
            # 查询测试节点
            result = session.run("MATCH (test:TestNode {name: 'ConnectionTest'}) RETURN test")
            if result.single():
                print("✅ 数据库写入/读取操作成功")
                
                # 清理测试数据
                session.run("MATCH (test:TestNode {name: 'ConnectionTest'}) DELETE test")
                print("✅ 测试数据清理完成")
                
            else:
                print("❌ 数据库读取失败")
                return False
                
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        return False


def test_http_hello_world(host=None, port=7474):
    """发送简单的 hello world 请求到 Neo4j HTTP 接口"""
    if host is None:
        host = SystemEnv.GRAPH_DB_HOST
    try:
        url = f"http://{host}:{port}"
        response = requests.get(url, timeout=5)
        print(f"🌍 HTTP Hello World 测试: {url}")
        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        if response.text:
            print(f"   响应内容: {response.text[:200]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ HTTP Hello World 失败: {e}")
        return False


def test_cypher_hello_world():
    """使用 GraphDbService 发送简单的 Cypher hello world 查询"""
    try:
        graph_db_service: GraphDbService = GraphDbService.instance
        graph_db = graph_db_service.get_default_graph_db()

        with graph_db.conn.session() as session:
            result = session.run(
                "RETURN 'Hello, Neo4j from Cypher!' as message, datetime() as timestamp"
            )
            record = result.single()
            message = record["message"]
            timestamp = record["timestamp"]

        print("🔗 Cypher Hello World 成功:")
        print(f"   消息: {message}")
        print(f"   时间戳: {timestamp}")
        return True

    except Exception as e:
        print(f"❌ Cypher Hello World 失败: {e}")
        return False


def main():
    """主测试函数"""

    print("🔍 开始测试Neo4j Docker容器连接...")
    print(f"📡 目标主机: {SystemEnv.GRAPH_DB_HOST}")
    print("=" * 50)

    # 先进行 Hello World 测试
    print("\n🌍 Hello World 测试")
    print("-" * 30)
    http_hello_success = test_http_hello_world()
    cypher_hello_success = test_cypher_hello_world()

    # 测试配置
    test_configs = [
        {
            "name": "主容器 (标准端口)",
            "http_port": 7474,
            "bolt_uri": f"bolt://{SystemEnv.GRAPH_DB_HOST}:7687",
        }
    ]
    
    success_count = 0
    
    for config in test_configs:
        print(f"\n📋 测试 {config['name']}")
        print("-" * 30)
        
        # 测试HTTP界面
        http_success = test_http_interface(port=config["http_port"])
        
        # 测试Bolt连接
        bolt_success = test_bolt_connection(config["bolt_uri"])
        
        # 如果Bolt连接成功，测试数据库操作
        if bolt_success:
            db_success = test_database_operations(config["bolt_uri"])
            if db_success:
                success_count += 1
                print(f"🎉 {config['name']} - 所有测试通过!")
            else:
                print(f"⚠️  {config['name']} - 连接成功但数据库操作失败")
        else:
            print(f"💥 {config['name']} - 连接失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试总结: {success_count}/{len(test_configs)} 个容器完全可用")
    print(f"🌍 Hello World 测试: HTTP={http_hello_success}, Cypher={cypher_hello_success}")
    
    if success_count == 0:
        print("🚨 所有容器都无法正常访问，请检查:")
        print("   1. Docker容器是否正在运行")
        print("   2. 端口映射是否正确")
        print("   3. Neo4j服务是否完全启动")
        print("   4. 防火墙设置")
        return 1
    else:
        print("✅ 至少有一个容器可以正常使用")
        return 0


if __name__ == "__main__":
    sys.exit(main())
