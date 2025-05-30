# 图数据库模式文档

本文档描述了 Weaver 系统中用于在 Neo4j 中存储体验数据的完整图数据库模式。

## 节点类型

### ExperientialScene（体验场景）
表示特定的体验场景或时刻。

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `scene_name` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字。示例：`kyoto_bamboo_forest_morning`，`beach_sunset_serenity` |
| `description` | STRING | 场景的核心描述（例如：'清晨薄雾笼罩的京都岚山竹林'） |
| `timestamp` | DATETIME | 场景发生的时间 |
| `location_text` | STRING | 场景位置的文本描述（例如：'Kyoto, Japan'）。可选 |
| `embed` | LIST OF FLOAT | scene_name 的嵌入向量表示 |

### FocalObservation（焦点观察）
表示在场景中注意到的特定观察或细节。

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `observation_name` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字。示例：`mossy_stone_detail`，`artisan_expression_focus` |
| `observed_element` | STRING | 观察到的特定元素的描述 |
| `significance` | STRING | 用户指定或 LLM 推断的重要性。可选 |
| `timestamp` | DATETIME | 进行或记录观察的时间 |
| `embed` | LIST OF FLOAT | observation_name 的嵌入向量表示 |

### AffectiveResonance（情感共鸣）
表示由体验触发的情感反应或感受。

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `resonance_name` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字。示例：`peaceful_feeling_by_lake`，`awe_at_mountain_view` |
| `emotion_label` | STRING | 核心情感标签（例如：'Peaceful'，'Excited'，'Awe'） |
| `trigger_description` | STRING | 触发这种情感的描述。可选 |
| `timestamp` | DATETIME | 体验或记录情感的时间 |
| `embed` | LIST OF FLOAT | resonance_name 的嵌入向量表示 |

### NarrativeAnchor（叙事锚点）
表示跨体验的反复出现的主题或叙事模式。

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `anchor_name` | STRING | **主键。** 唂一标识符，小写字母加下划线，无数字。示例：`theme_of_solitude`，`pattern_of_discovery` |
| `theme_summary` | STRING | 反复出现主题的简要总结（例如：'The Beauty of Solitude'） |
| `pattern_description` | STRING | 对这种叙事模式的进一步解释或背景。可选 |
| `timestamp` | DATETIME | 创建或最后更新锚点的时间 |
| `embed` | LIST OF FLOAT | anchor_name 的嵌入向量表示 |

### InteractionPoint（互动点）
表示与人、物体或环境的互动。

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `interaction_name` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字。示例：`chat_with_local_guide`，`tasting_street_food_item` |
| `action_description` | STRING | 互动的描述 |
| `outcome_summary` | STRING | 互动结果或感受的简要总结。可选 |
| `timestamp` | DATETIME | 互动发生的时间 |
| `embed` | LIST OF FLOAT | interaction_name 的嵌入向量表示 |

### DigitalAsset（数字资产）
表示记录体验的数字文件（图像、视频、音频、文本）。

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `asset_name` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字。示例：`img_paris_eiffel_tower`，`note_travel_journal_day_one` |
| `description` | STRING | 数字资产的描述 |
| `file_id` | STRING | 原始数字文件的 ID 引用 |
| `media_type` | STRING | 媒体类型：'image'，'video'，'audio'，'text' |
| `timestamp` | DATETIME | 资产的原始创建时间戳 |
| `embed` | LIST OF FLOAT | asset_name 的嵌入向量表示 |

### City（城市）
表示体验发生的城市。

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `city_name` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字。示例：`hangzhou`，`shanghai`，`beijing` |
| `chinese_name` | STRING | 城市的中文名称（例如：'杭州'，'上海'，'北京'） |
| `description` | STRING | 城市的描述。可选 |
| `embed` | LIST OF FLOAT | city_name 的嵌入向量表示 |

### Province（省份）
表示省份或行政区域。

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `province_name` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字。示例：`zhejiang`，`jiangsu`，`guangdong` |
| `chinese_name` | STRING | 省份的中文名称（例如：'浙江省'，'江苏省'，'广东省'） |
| `description` | STRING | 省份的描述。可选 |
| `embed` | LIST OF FLOAT | province_name 的嵌入向量表示 |

### Season（季节）
表示体验的季节背景。

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `season_name` | STRING | **主键。** 小写季节名称。示例：`spring`，`summer`，`autumn`，`winter` |
| `chinese_name` | STRING | 季节的中文名称（例如：'春天'，'夏天'，'秋天'，'冬天'） |
| `description` | STRING | 季节特征的描述。可选 |
| `embed` | LIST OF FLOAT | season_name 的嵌入向量表示 |

## 关系类型

### OBSERVED_IN（观察于）
将焦点观察连接到发生观察的体验场景。

**方向：** `FocalObservation → ExperientialScene`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |
| `timestamp_in_scene` | DATETIME | 场景中观察的具体时间戳。可选 |

### TRIGGERED_BY（被触发）
将情感共鸣连接到其触发元素。

**方向：** `AffectiveResonance → [ExperientialScene, FocalObservation, InteractionPoint]`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |

### OCCURRED_DURING（发生于）
将互动点连接到发生互动的体验场景。

**方向：** `InteractionPoint → ExperientialScene`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |

### CONTRIBUTES_TO（贡献于）
将各种体验片段连接到它们支持的更广泛的叙事锚点。

**方向：** `[ExperientialScene, FocalObservation, AffectiveResonance, InteractionPoint] → NarrativeAnchor`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |

### CONSTRUCTED_FROM_ASSET（从资产构建）
将体验场景连接到派生它的数字资产。

**方向：** `ExperientialScene → DigitalAsset`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |

### IDENTIFIED_IN_ASSET（在资产中识别）
将焦点观察连接到识别它的数字资产。

**方向：** `FocalObservation → DigitalAsset`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |
| `roi_coordinates` | STRING | 资产内的感兴趣区域坐标（例如：'x,y,w,h'）。可选 |

### EXTRACTED_FROM_ASSET（从资产提取）
将情感共鸣连接到提取它的数字资产。

**方向：** `AffectiveResonance → DigitalAsset`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |
| `text_snippet` | STRING | 来自资产的相关文本片段。可选 |

### DOCUMENTED_BY_ASSET（被资产记录）
将互动点连接到记录它的数字资产。

**方向：** `InteractionPoint → DigitalAsset`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |

### LOCATED_IN_CITY（位于城市）
将体验场景连接到发生的城市。

**方向：** `ExperientialScene → City`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |

### BELONGS_TO_PROVINCE（属于省份）
将城市连接到其所在省份。

**方向：** `City → Province`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |

### OCCURRED_IN_SEASON（发生于季节）
将体验场景连接到发生的季节。

**方向：** `ExperientialScene → Season`

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| `id` | STRING | **主键。** 唯一标识符，小写字母加下划线，无数字 |

## 关键设计原则

### 主键命名约定
- 所有主键必须仅使用英文
- 使用小写字母，用下划线分隔单词
- 主键中不能有数字
- 应该是描述性的、人类可读的

### 嵌入向量
- 所有节点都包含 LIST OF FLOAT 类型的 `embed` 属性
- 向量有 1024 个维度，使用余弦相似度
- 从主键或描述文本生成

### 时间戳
- 所有时间戳使用 Neo4j DATETIME 格式
- 应该使用 ISO 8601 格式以确保兼容性
- 表示事件发生或记录的时间

### 可选属性
- 许多描述性属性标记为可选
- 核心标识属性（主键）始终是必需的
- 关系属性通常是可选的，除了 ID

## 图模式

### 核心体验模式
```
(DigitalAsset)-[CONSTRUCTED_FROM_ASSET]-(ExperientialScene)-[LOCATED_IN_CITY]-(City)-[BELONGS_TO_PROVINCE]-(Province)
(ExperientialScene)-[OCCURRED_IN_SEASON]-(Season)
(FocalObservation)-[OBSERVED_IN]-(ExperientialScene)
(AffectiveResonance)-[TRIGGERED_BY]-(ExperientialScene)
(InteractionPoint)-[OCCURRED_DURING]-(ExperientialScene)
```

### 叙事模式
```
([ExperientialScene, FocalObservation, AffectiveResonance, InteractionPoint])-[CONTRIBUTES_TO]-(NarrativeAnchor)
```

### 资产记录模式
```
(FocalObservation)-[IDENTIFIED_IN_ASSET]-(DigitalAsset)
(AffectiveResonance)-[EXTRACTED_FROM_ASSET]-(DigitalAsset)
(InteractionPoint)-[DOCUMENTED_BY_ASSET]-(DigitalAsset)
```
