import socket

from chat2graph.core.common.system_env import SystemEnv


def check_port(host, port, timeout=3):
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def quick_check():
    """快速检查所有Neo4j端口"""
    ports_to_check = [(7474, "HTTP - 主容器"), (7687, "Bolt - 主容器")]
    
    print("🔍 快速端口检查...")
    print(f"📡 目标主机: {SystemEnv.GRAPH_DB_HOST}")

    for port, description in ports_to_check:
        is_open = check_port(SystemEnv.GRAPH_DB_HOST, port)
        status = "✅ 开放" if is_open else "❌ 关闭"
        print(f"   端口 {port:5d} ({description:15s}): {status}")


if __name__ == "__main__":
    quick_check()
