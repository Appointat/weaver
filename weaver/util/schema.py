from typing import Any, Dict, List

from chat2graph.core.service.graph_db_service import GraphDbService


def generate_schema_cypher_commands(schema: Dict[str, Any]) -> List[str]:
    """
    Generate Cypher commands to create the graph schema in Neo4j.

    Args:
        schema: The schema definition dictionary

    Returns:
        List of Cypher commands to execute
    """
    commands = []

    # 1. Generate commands for nodes
    for node_label, node_def in schema.get("nodes", {}).items():
        primary_key = node_def.get("primary_key", "id")

        # Create constraint on primary key (ensure uniqueness)
        # Updated syntax for Neo4j 5.x
        commands.append(
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node_label}) REQUIRE n.{primary_key} IS UNIQUE"
        )

        # Create indexes for properties that might be searched frequently
        properties = node_def.get("properties", [])
        for prop in properties:
            prop_name = prop.get("name")
            prop_type = prop.get("type")

            # Create vector index for embed property with proper configuration
            if prop_name == "embed" and prop_type == "LIST OF FLOAT":
                commands.append(
                    f"CREATE VECTOR INDEX {node_label.lower()}_embed_vector_index "
                    f"FOR (n:{node_label}) ON (n.{prop_name}) "
                    "OPTIONS { indexConfig: {`vector.dimensions`: 1024, `vector.similarity_function`: 'cosine'} }"
                )
                continue

            # Create regular index for other properties
            commands.append(f"CREATE INDEX IF NOT EXISTS FOR (n:{node_label}) ON (n.{prop_name})")

    # 2. Generate commands for relationships
    for rel_type, rel_def in schema.get("relationships", {}).items():
        primary_key = rel_def.get("primary_key", "id")

        # Create constraint for relationship ID uniqueness
        # Updated syntax for Neo4j 5.x
        commands.append(
            f"CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:{rel_type}]-() REQUIRE r.{primary_key} IS UNIQUE"
        )

        # Generate commands to ensure relationship connectivity rules
        source_labels = rel_def.get("source_vertex_labels", [])
        target_labels = rel_def.get("target_vertex_labels", [])

        for source in source_labels:
            for target in target_labels:
                # Add a comment describing the allowed connection
                commands.append(f"// Relationship {rel_type} is allowed from {source} to {target}")

    return commands


def import_graph_schema() -> None:
    """
    Imports the predefined global graph schema (PREDEFINED_GRAPH_SCHEMA)
    into the configured graph database via the graph_db_service.

    This function retrieves the default graph database configuration and then
    calls the update_schema_metadata method, passing the complete predefined
    schema. This is intended to set or overwrite the schema in the database.
    """
    try:
        graph_db_service: GraphDbService = GraphDbService.instance
        graph_db_config = graph_db_service.get_default_graph_db_config()

        # The update_schema_metadata function is responsible for how the schema is updated.
        # Passing the complete PREDEFINED_GRAPH_SCHEMA aims to replace the existing schema
        # with this new definition.
        graph_db_service.update_schema_metadata(
            graph_db_config=graph_db_config, schema=PREDEFINED_GRAPH_SCHEMA
        )

        # Generate Cypher commands to create schema in Neo4j
        cypher_commands = generate_schema_cypher_commands(PREDEFINED_GRAPH_SCHEMA)

        # Execute each command using Neo4j connection
        graph_db = graph_db_service.get_default_graph_db()
        with graph_db.conn.session() as session:
            for command in cypher_commands:
                # Skip comments
                if command.startswith("//"):
                    print(command)
                    continue

                print(f"Executing: {command}")
                session.run(command)

        print("Graph schema imported/updated successfully using PREDEFINED_GRAPH_SCHEMA.")
    except ValueError as e:
        print(f"Error during graph schema import: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during graph schema import: {e}")


# Defines the comprehensive graph schema as a global variable.
# This schema will be used to overwrite the existing schema in the graph database.
PREDEFINED_GRAPH_SCHEMA: Dict[str, Any] = {
    "nodes": {
        "ExperientialScene": {
            "primary_key": "scene_name",
            "properties": [
                {
                    "name": "scene_name",
                    "type": "STRING",
                    "desc": "Unique identifier for the ExperientialScene node, should be the name in lowercase, connected by underscores, without numbers. Primary key must be in English only. Examples: `kyoto_bamboo_forest_morning`, `beach_sunset_serenity`.",
                },
                {
                    "name": "description",
                    "type": "STRING",
                    "desc": "LLM-generated or user-inputted core description of the scene (e.g., '清晨薄雾笼罩的京都岚山竹林').",
                },
                {
                    "name": "timestamp",
                    "type": "DATETIME",
                    "desc": "Timestamp indicating when the ExperientialScene occurred.",
                },
                {
                    "name": "location_text",
                    "type": "STRING",
                    "desc": "Textual description of the scene's location (e.g., 'Kyoto, Japan'). Optional.",
                },
                {
                    "name": "embed",
                    "type": "LIST OF FLOAT",
                    "desc": "Embedding vector representation of the node's primary key (scene_name).",
                },
            ],
        },
        "FocalObservation": {
            "primary_key": "observation_name",
            "properties": [
                {
                    "name": "observation_name",
                    "type": "STRING",
                    "desc": "Unique identifier for the FocalObservation node, should be the name in lowercase, connected by underscores, without numbers. Primary key must be in English only. Examples: `mossy_stone_detail`, `artisan_expression_focus`.",
                },
                {
                    "name": "observed_element",
                    "type": "STRING",
                    "desc": "Description of the specific element observed (e.g., 'a uniquely shaped mossy stone').",
                },
                {
                    "name": "significance",
                    "type": "STRING",
                    "desc": "User-assigned or LLM-inferred significance of the observation. Optional.",
                },
                {
                    "name": "timestamp",
                    "type": "DATETIME",
                    "desc": "Timestamp indicating when the FocalObservation was made or recorded.",
                },
                {
                    "name": "embed",
                    "type": "LIST OF FLOAT",
                    "desc": "Embedding vector representation of the node's primary key (observation_name).",
                },
            ],
        },
        "AffectiveResonance": {
            "primary_key": "resonance_name",
            "properties": [
                {
                    "name": "resonance_name",
                    "type": "STRING",
                    "desc": "Unique identifier for the AffectiveResonance node, should be the name in lowercase, connected by underscores, without numbers. Primary key must be in English only. Examples: `peaceful_feeling_by_lake`, `awe_at_mountain_view`.",
                },
                {
                    "name": "emotion_label",
                    "type": "STRING",
                    "desc": "Core emotion label (e.g., 'Peaceful', 'Excited', 'Awe').",
                },
                {
                    "name": "trigger_description",
                    "type": "STRING",
                    "desc": "Description of what specifically triggered this emotion or thought. Optional.",
                },
                {
                    "name": "timestamp",
                    "type": "DATETIME",
                    "desc": "Timestamp indicating when the AffectiveResonance was experienced or logged.",
                },
                {
                    "name": "embed",
                    "type": "LIST OF FLOAT",
                    "desc": "Embedding vector representation of the node's primary key (resonance_name).",
                },
            ],
        },
        "NarrativeAnchor": {
            "primary_key": "anchor_name",
            "properties": [
                {
                    "name": "anchor_name",
                    "type": "STRING",
                    "desc": "Unique identifier for the NarrativeAnchor node, should be the name in lowercase, connected by underscores, without numbers. Primary key must be in English only. Examples: `theme_of_solitude`, `pattern_of_discovery`.",
                },
                {
                    "name": "theme_summary",
                    "type": "STRING",
                    "desc": "Brief summary of the recurring theme or narrative thread (e.g., 'The Beauty of Solitude').",
                },
                {
                    "name": "pattern_description",
                    "type": "STRING",
                    "desc": "Further explanation or context for this narrative pattern. Optional.",
                },
                {
                    "name": "timestamp",
                    "type": "DATETIME",
                    "desc": "Timestamp indicating when the NarrativeAnchor was created or last updated.",
                },
                {
                    "name": "embed",
                    "type": "LIST OF FLOAT",
                    "desc": "Embedding vector representation of the node's primary key (anchor_name).",
                },
            ],
        },
        "InteractionPoint": {
            "primary_key": "interaction_name",
            "properties": [
                {
                    "name": "interaction_name",
                    "type": "STRING",
                    "desc": "Unique identifier for the InteractionPoint node, should be the name in lowercase, connected by underscores, without numbers. Primary key must be in English only. Examples: `chat_with_local_guide`, `tasting_street_food_item`.",
                },
                {
                    "name": "action_description",
                    "type": "STRING",
                    "desc": "Description of the interaction (e.g., 'chatted with a local artisan', 'tasted a local delicacy').",
                },
                {
                    "name": "outcome_summary",
                    "type": "STRING",
                    "desc": "Brief summary of the interaction's outcome or feeling. Optional.",
                },
                {
                    "name": "timestamp",
                    "type": "DATETIME",
                    "desc": "Timestamp indicating when the InteractionPoint occurred.",
                },
                {
                    "name": "embed",
                    "type": "LIST OF FLOAT",
                    "desc": "Embedding vector representation of the node's primary key (interaction_name).",
                },
            ],
        },
        "DigitalAsset": {
            "primary_key": "asset_name",
            "properties": [
                {
                    "name": "asset_name",
                    "type": "STRING",
                    "desc": "Unique identifier for the DigitalAsset node, should be the name in lowercase, connected by underscores, without numbers. Primary key must be in English only. Examples: `img_paris_eiffel_tower`, `note_travel_journal_day_one`.",
                },
                {
                    "name": "description",
                    "type": "STRING",
                    "desc": "Description of the digital asset (e.g., 'Photo of the Eiffel Tower in Paris').",
                },
                {
                    "name": "file_id",
                    "type": "STRING",
                    "desc": "id to the original digital file.",
                },
                {
                    "name": "media_type",
                    "type": "STRING",
                    "desc": "Type of the media (e.g., 'image', 'video', 'audio', 'text'). Enum stored as STRING.",
                },
                {
                    "name": "timestamp",
                    "type": "DATETIME",
                    "desc": "Original creation timestamp of the DigitalAsset.",
                },
                {
                    "name": "embed",
                    "type": "LIST OF FLOAT",
                    "desc": "Embedding vector representation of the node's primary key (asset_name).",
                },
            ],
        },
        "City": {
            "primary_key": "city_name",
            "properties": [
                {
                    "name": "city_name",
                    "type": "STRING",
                    "desc": "Unique identifier for the City node, should be the name in lowercase, connected by underscores, without numbers. Primary key must be in English only. Examples: `hangzhou`, `shanghai`, `beijing`.",
                },
                {
                    "name": "chinese_name",
                    "type": "STRING",
                    "desc": "Chinese name of the city (e.g., '杭州', '上海', '北京').",
                },
                {
                    "name": "description",
                    "type": "STRING",
                    "desc": "Description of the city (e.g., 'Beautiful city known for West Lake'). Optional.",
                },
                {
                    "name": "embed",
                    "type": "LIST OF FLOAT",
                    "desc": "Embedding vector representation of the node's primary key (city_name).",
                },
            ],
        },
        "Province": {
            "primary_key": "province_name",
            "properties": [
                {
                    "name": "province_name",
                    "type": "STRING",
                    "desc": "Unique identifier for the Province node, should be the name in lowercase, connected by underscores, without numbers. Primary key must be in English only. Examples: `zhejiang`, `jiangsu`, `guangdong`.",
                },
                {
                    "name": "chinese_name",
                    "type": "STRING",
                    "desc": "Chinese name of the province (e.g., '浙江省', '江苏省', '广东省').",
                },
                {
                    "name": "description",
                    "type": "STRING",
                    "desc": "Description of the province (e.g., 'Eastern coastal province known for scenic beauty'). Optional.",
                },
                {
                    "name": "embed",
                    "type": "LIST OF FLOAT",
                    "desc": "Embedding vector representation of the node's primary key (province_name).",
                },
            ],
        },
        "Season": {
            "primary_key": "season_name",
            "properties": [
                {
                    "name": "season_name",
                    "type": "STRING",
                    "desc": "Unique identifier for the Season node, should be the name in lowercase. Primary key must be in English only. Examples: `spring`, `summer`, `autumn`, `winter`.",
                },
                {
                    "name": "chinese_name",
                    "type": "STRING",
                    "desc": "Chinese name of the season (e.g., '春天', '夏天', '秋天', '冬天').",
                },
                {
                    "name": "description",
                    "type": "STRING",
                    "desc": "Description of the season characteristics (e.g., 'Warm weather with blooming flowers'). Optional.",
                },
                {
                    "name": "embed",
                    "type": "LIST OF FLOAT",
                    "desc": "Embedding vector representation of the node's primary key (season_name).",
                },
            ],
        },
    },
    "relationships": {
        "OBSERVED_IN": {
            "primary_key": "id",
            "desc": "Connects a FocalObservation to the ExperientialScene it occurred in.",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the OBSERVED_IN relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `obs_one_in_scene_alpha`, `detail_linked_to_main_view`.",
                },
                {
                    "name": "timestamp_in_scene",
                    "type": "DATETIME",
                    "desc": "Specific timestamp of the observation within the scene. Optional.",
                },
            ],
            "source_vertex_labels": ["FocalObservation"],
            "target_vertex_labels": ["ExperientialScene"],
        },
        "TRIGGERED_BY": {
            "primary_key": "id",
            "desc": "Connects an AffectiveResonance to its triggering element (Scene, Observation, or Interaction).",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the TRIGGERED_BY relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `emotion_from_scene_beta`, `feeling_sparked_by_observation`.",
                }
            ],
            "source_vertex_labels": ["AffectiveResonance"],
            "target_vertex_labels": ["ExperientialScene", "FocalObservation", "InteractionPoint"],
        },
        "OCCURRED_DURING": {
            "primary_key": "id",
            "desc": "Connects an InteractionPoint to the ExperientialScene it happened within.",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the OCCURRED_DURING relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `interaction_during_event_gamma`, `action_within_context`.",
                }
            ],
            "source_vertex_labels": ["InteractionPoint"],
            "target_vertex_labels": ["ExperientialScene"],
        },
        "CONTRIBUTES_TO": {
            "primary_key": "id",
            "desc": "Connects various experiential fragments to a broader NarrativeAnchor they support or exemplify.",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the CONTRIBUTES_TO relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `scene_supports_theme_delta`, `observation_builds_narrative`.",
                }
            ],
            "source_vertex_labels": [
                "ExperientialScene",
                "FocalObservation",
                "AffectiveResonance",
                "InteractionPoint",
            ],
            "target_vertex_labels": ["NarrativeAnchor"],
        },
        "CONSTRUCTED_FROM_ASSET": {
            "primary_key": "id",
            "desc": "Connects an ExperientialScene to the DigitalAsset(s) it was derived from.",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the CONSTRUCTED_FROM_ASSET relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `scene_derived_from_photo_epsilon`, `experience_built_on_note`.",
                }
            ],
            "source_vertex_labels": ["ExperientialScene"],
            "target_vertex_labels": ["DigitalAsset"],
        },
        "IDENTIFIED_IN_ASSET": {
            "primary_key": "id",
            "desc": "Connects a FocalObservation to the DigitalAsset where it was identified.",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the IDENTIFIED_IN_ASSET relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `observation_in_image_zeta`, `detail_found_in_video_segment`.",
                },
                {
                    "name": "roi_coordinates",
                    "type": "STRING",
                    "desc": "Region of Interest coordinates (e.g., 'x,y,w,h') within the asset. Optional.",
                },
            ],
            "source_vertex_labels": ["FocalObservation"],
            "target_vertex_labels": ["DigitalAsset"],
        },
        "EXTRACTED_FROM_ASSET": {
            "primary_key": "id",
            "desc": "Connects an AffectiveResonance (from text) to the DigitalAsset it was extracted from.",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the EXTRACTED_FROM_ASSET relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `emotion_from_text_eta`, `feeling_pulled_from_journal_entry`.",
                },
                {
                    "name": "text_snippet",
                    "type": "STRING",
                    "desc": "Relevant text snippet from the asset. Optional.",
                },
            ],
            "source_vertex_labels": ["AffectiveResonance"],
            "target_vertex_labels": ["DigitalAsset"],
        },
        "DOCUMENTED_BY_ASSET": {
            "primary_key": "id",
            "desc": "Connects an InteractionPoint to a DigitalAsset that documents it. Optional.",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the DOCUMENTED_BY_ASSET relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `interaction_recorded_in_audio_theta`, `event_captured_by_video`.",
                }
            ],
            "source_vertex_labels": ["InteractionPoint"],
            "target_vertex_labels": ["DigitalAsset"],
        },
        "LOCATED_IN_CITY": {
            "primary_key": "id",
            "desc": "Connects an ExperientialScene to the City where it occurred.",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the LOCATED_IN_CITY relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `scene_in_hangzhou`, `experience_at_shanghai`.",
                }
            ],
            "source_vertex_labels": ["ExperientialScene"],
            "target_vertex_labels": ["City"],
        },
        "BELONGS_TO_PROVINCE": {
            "primary_key": "id",
            "desc": "Connects a City to its Province.",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the BELONGS_TO_PROVINCE relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `hangzhou_in_zhejiang`, `shanghai_in_shanghai_municipality`.",
                }
            ],
            "source_vertex_labels": ["City"],
            "target_vertex_labels": ["Province"],
        },
        "OCCURRED_IN_SEASON": {
            "primary_key": "id",
            "desc": "Connects an ExperientialScene to the Season when it occurred.",
            "properties": [
                {
                    "name": "id",
                    "type": "STRING",
                    "desc": "Unique identifier for the OCCURRED_IN_SEASON relationship instance, should be the name in lowercase, connected by underscores, without numbers. Examples: `scene_in_spring`, `experience_during_autumn`.",
                }
            ],
            "source_vertex_labels": ["ExperientialScene"],
            "target_vertex_labels": ["Season"],
        },
    },
}
