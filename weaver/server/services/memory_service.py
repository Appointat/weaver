from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from chat2graph.core.sdk.agentic_service import AgenticService

from weaver.build_memory import process_single_memory
from weaver.util.schema import import_graph_schema


class MemoryService:
    """记忆处理服务 - 对应HTML页面的各种记忆功能"""

    def __init__(self):
        self.mas = AgenticService.load("weaver.yml")

        # 内存存储 (生产环境应使用数据库)
        self._memories: Dict[str, Dict[str, Any]] = {}

    def create_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新记忆 - 对应页面的"开始编织记忆"功能

        将用户提供的旅行数据转换为结构化的记忆对象，包含AI生成的叙述、洞察和相册内容。

        参数:
            data (Dict[str, Any]): 旅行数据字典，包含以下字段:
                - tripName (str): 旅程名称，如"京都秋日私语"
                - location (str): 地点信息，如"清水寺, 京都, 日本"
                - startDate (str): 开始日期，格式"YYYY-MM-DD"
                - endDate (str, optional): 结束日期，格式"YYYY-MM-DD"
                - notes (str): 用户的旅行笔记内容
                - music (str, optional): 背景音乐信息
                - photosCount (int, optional): 上传的照片数量，默认为0
                - uploadedFiles (List, optional): 上传的文件信息列表
                - fileIds (List, optional): 用于AI处理的文件ID列表

        返回:
            Dict[str, Any]: 完整的记忆对象，包含:
                - id (str): 唯一记忆标识符
                - tripName (str): 旅程名称
                - location (str): 地点信息
                - startDate (str): 开始日期
                - endDate (str): 结束日期
                - notes (str): 用户笔记
                - music (str): 背景音乐
                - photosCount (int): 照片数量
                - narrative (str): AI生成的回忆叙述
                - insights (Dict): AI分析的洞察信息
                  - themes (List[str]): 主要主题标签
                  - emotions (List[str]): 情感倾向
                  - recommendation (str): 未来建议
                - tags (List[str]): 自动提取的标签列表
                - album (Dict): 多媒体相册数据
                  - items (List): 相册项目列表
                  - count (int): 项目总数
                - createdAt (str): 创建时间 (ISO格式)
                - sessionId (str): 会话ID
                - enhancedNarrative (None): 增强叙述(初始为None)
        """
        try:
            import_graph_schema()
        except Exception as e:
            print(f"Warning: Could not import graph schema: {e}")

        memory_id = str(uuid4())
        session_id = str(uuid4())

        # 提取旅行数据
        trip_name = data.get("tripName", "")
        location = data.get("location", "")
        start_date = data.get("startDate", "")
        end_date = data.get("endDate", "")
        notes = data.get("notes", "")
        music = data.get("music", "")
        photos_count = data.get("photosCount", 0)

        # 生成AI叙述
        ai_narrative = process_single_memory(data, data.get("fileIds", []))

        # 创建记忆对象
        memory = {
            "id": memory_id,
            "tripName": trip_name,
            "location": location,
            "startDate": start_date,
            "endDate": end_date,
            "notes": notes,
            "music": music,
            "photosCount": photos_count,
            "narrative": ai_narrative,
            "insights": self._generate_insights(trip_name, location, notes),
            "tags": self._generate_tags(trip_name, location, notes),
            "album": self._generate_album_data(data),
            "createdAt": datetime.now().isoformat(),
            "sessionId": session_id,
            "enhancedNarrative": None,
        }

        # 存储记忆
        self._memories[memory_id] = memory

        return memory

    def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取特定记忆

        根据记忆ID检索完整的记忆对象。

        参数:
            memory_id (str): 记忆的唯一标识符

        返回:
            Optional[Dict[str, Any]]: 记忆对象，如果未找到则返回None
        """
        return self._memories.get(memory_id)

    def get_memory_album(self) -> List[str]:
        """获取记忆相册 - 对应页面的多媒体记忆相册功能

        提取指定记忆的相册数据，包含笔记、图片、音乐等多媒体内容。

        参数:
            memory_id (str): 记忆的唯一标识符

        返回:
            Optional[Dict[str, Any]]: 相册数据对象，包含:
                - items (List): 相册项目列表，每个项目包含:
                  - type (str): 项目类型 ('note', 'image', 'music')
                  - title (str): 项目标题
                  - content (str, optional): 项目内容
                  - icon (str): Font Awesome图标类名
                  - placeholder (bool, optional): 是否为占位符
                - count (int): 项目总数

            如果记忆不存在则返回None
        """
        from weaver.get_ablum import get_digital_asset_file_contents

        return get_digital_asset_file_contents()

    def _generate_insights(self, trip_name: str, location: str, notes: str) -> Dict[str, Any]:
        """生成AI洞察"""
        # 基于内容分析主题
        themes = ['探索发现', '文化体验']
        if '自然' in notes or '山' in notes or '海' in notes:
            themes.append('自然美景')
        if '历史' in notes or '建筑' in notes:
            themes.append('历史文化')
        if '美食' in notes or '味道' in notes:
            themes.append('美食体验')
        
        # 分析情感
        emotions = ['愉悦']
        if '感动' in notes or '震撼' in notes:
            emotions.append('感动')
        if '宁静' in notes or '平静' in notes:
            emotions.append('宁静')
        if '兴奋' in notes or '激动' in notes:
            emotions.append('兴奋')
        
        # 生成建议
        recommendations = [
            '下次可以尝试在当地停留更长时间，深度体验当地文化',
            '建议携带更专业的摄影设备记录美好瞬间',
            '可以考虑学习一些当地语言，增进与当地人的交流',
            '建议提前了解当地的历史文化背景，会有更深的体验'
        ]
        
        import random
        recommendation = random.choice(recommendations)
        
        return {
            'themes': themes[:3],  # 最多3个主题
            'emotions': emotions[:2],  # 最多2个情感
            'recommendation': recommendation
        }
    
    def _generate_tags(self, trip_name: str, location: str, notes: str) -> List[str]:
        """生成标签"""
        tags = ['旅行']
        
        # 添加旅程名称标签
        if trip_name:
            tags.append(trip_name[:10])
        
        # 添加地点标签
        if location:
            location_parts = [part.strip() for part in location.split(',')]
            tags.extend([part[:10] for part in location_parts[:3]])
        
        # 从笔记中提取关键词
        keywords = ['美景', '文化', '美食', '建筑', '自然', '历史', '海滩', '山脉', '城市', '乡村']
        for keyword in keywords:
            if keyword in notes:
                tags.append(keyword)
        
        return list(set(tag for tag in tags if tag.strip()))
    
    def _generate_album_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成相册数据"""
        album_items = []
        
        # 添加笔记项
        if data.get('notes'):
            album_items.append({
                'type': 'note',
                'title': '我的笔记片段',
                'content': data['notes'][:200] + ('...' if len(data['notes']) > 200 else ''),
                'icon': 'fas fa-sticky-note'
            })
        
        # 添加图片项（模拟）
        photos_count = data.get('photosCount', 0)
        for i in range(min(photos_count, 3)):
            album_items.append({
                'type': 'image',
                'title': f'旅行照片 {i + 1}',
                'placeholder': True,
                'icon': 'fas fa-image'
            })
        
        # 添加音乐项
        if data.get('music'):
            album_items.append({
                'type': 'music',
                'title': '背景旋律',
                'content': f'当时聆听: {data["music"]}',
                'icon': 'fas fa-music'
            })
        
        return {
            'items': album_items,
            'count': len(album_items)
        }
