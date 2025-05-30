import os
from pathlib import Path


def create_chat2graph_structure():
    """在/root下创建chat2graph的目录结构和数据库"""

    # 基础路径 (在root用户下会是 /root/.chat2graph)
    base_path = "/root/.chat2graph"

    # 需要创建的目录
    directories = [
        base_path,
        f"{base_path}/system",
        f"{base_path}/files",
        f"{base_path}/knowledge_bases",
    ]

    # 创建所有目录
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

    # 设置权限
    os.chmod(base_path, 0o755)
    for directory in directories:
        os.chmod(directory, 0o755)

    print(f"\n✓ Chat2Graph structure created successfully at: {base_path}")
    return base_path


if __name__ == "__main__":
    create_chat2graph_structure()
