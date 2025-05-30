from datetime import datetime, timedelta
import pathlib
import random

# 目标目录
target_dir = pathlib.Path("asset/text_data_v1")

# 确保目录存在
if not target_dir.exists():
    print(f"目录不存在: {target_dir}")
    exit(1)

# 获取当前时间作为基准
base_time = datetime.now()

# 遍历所有txt文件
txt_files = list(target_dir.glob("*.txt"))
print(f"找到 {len(txt_files)} 个文本文件")

for i, file_path in enumerate(txt_files):
    try:
        # 为每个文件生成略有不同的时间戳（按顺序往前推几小时到几天）
        time_offset = timedelta(hours=random.randint(1, 72))
        file_time = base_time - time_offset

        # 格式化为Neo4j DATETIME格式 (ISO 8601)
        neo4j_datetime = file_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # 读取文件内容
        with open(file_path, encoding="utf-8") as file:
            content = file.read().rstrip()

        # 添加时间戳并写回文件
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
            file.write(f"\n\ndatetime({neo4j_datetime})")

        print(f"已处理文件 {file_path.name} - 添加时间戳: {neo4j_datetime}")

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")

print("处理完成!")
