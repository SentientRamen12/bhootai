import json
from src.data.database import get_sqlite_connection, get_chromadb_client
import uuid

# Player CRUD
def create_player(name, health=100, sanity=100, location_id=None):
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO player (name, health, sanity, current_location_id) VALUES (?, ?, ?, ?)",
        (name, health, sanity, location_id)
    )
    player_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return player_id

def get_player(player_id):
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM player WHERE id = ?", (player_id,))
    player = cursor.fetchone()
    conn.close()
    return player

def update_player_location(player_id, location_id):
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE player SET current_location_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (location_id, player_id)
    )
    conn.commit()
    conn.close()

# Location CRUD
def create_location(name, description, properties=None):
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    props_json = json.dumps(properties) if properties else None
    cursor.execute(
        "INSERT INTO location (name, description, properties) VALUES (?, ?, ?)",
        (name, description, props_json)
    )
    location_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return location_id

def get_location(location_id):
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM location WHERE id = ?", (location_id,))
    location = cursor.fetchone()
    conn.close()
    return location

def get_all_locations():
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM location")
    locations = cursor.fetchall()
    conn.close()
    return locations

# Entity CRUD
def create_entity(name, entity_type, description, location_id, properties=None):
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    props_json = json.dumps(properties) if properties else None
    cursor.execute(
        "INSERT INTO entity (name, type, description, location_id, properties) VALUES (?, ?, ?, ?, ?)",
        (name, entity_type, description, location_id, props_json)
    )
    entity_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entity_id

def get_entities_by_location(location_id):
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entity WHERE location_id = ?", (location_id,))
    entities = cursor.fetchall()
    conn.close()
    return entities

def get_entities_by_type(entity_type):
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entity WHERE type = ?", (entity_type,))
    entities = cursor.fetchall()
    conn.close()
    return entities

# GameState CRUD
def create_game_state(plot_progress=None, session_data=None, world_state=None):
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO game_state (current_plot_progress, session_data, world_state) VALUES (?, ?, ?)",
        (plot_progress, json.dumps(session_data), json.dumps(world_state))
    )
    state_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return state_id

def get_current_game_state():
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM game_state ORDER BY id DESC LIMIT 1")
    state = cursor.fetchone()
    conn.close()
    return state

def update_game_state(state_id, plot_progress=None, session_data=None, world_state=None):
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    updates = []
    values = []
    if plot_progress is not None:
        updates.append("current_plot_progress = ?")
        values.append(plot_progress)
    if session_data is not None:
        updates.append("session_data = ?")
        values.append(json.dumps(session_data))
    if world_state is not None:
        updates.append("world_state = ?")
        values.append(json.dumps(world_state))
    
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(state_id)
        cursor.execute(f"UPDATE game_state SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    conn.close()

# Memory CRUD
def add_episodic_memory(content, metadata=None):
    client = get_chromadb_client()
    collection = client.get_collection("episodic_memory")
    
    # Generate unique ID for the memory
    memory_id = str(uuid.uuid4())
    
    # Simple embedding (you might want to use a proper embedding model later)
    embedding = [0.0] * 384  # Placeholder embedding
    
    collection.add(
        ids=[memory_id],
        documents=[content],
        embeddings=[embedding],
        metadatas=[metadata or {}]
    )

def search_episodic_memory(query, n_results=5):
    client = get_chromadb_client()
    collection = client.get_collection("episodic_memory")
    
    # Simple embedding (you might want to use a proper embedding model later)
    query_embedding = [0.0] * 384  # Placeholder embedding
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results 