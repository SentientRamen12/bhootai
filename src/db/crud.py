import json
import sqlite3
from typing import List, Dict, Optional, Any
from src.db.database import get_sqlite_connection, get_chromadb_client

# Game State Operations
def create_game_state(plot_progress: str, session_data: Dict, world_state: Dict):
    """Create a new game state"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO game_states (plot_progress, session_data, world_state)
        VALUES (?, ?, ?)
    """, (plot_progress, json.dumps(session_data), json.dumps(world_state)))
    
    conn.commit()
    conn.close()

def get_current_game_state():
    """Get the most recent game state"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM game_states 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    conn.close()
    return result

def update_game_state(plot_progress: str, session_data: Dict, world_state: Dict):
    """Update the current game state"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE game_states 
        SET plot_progress = ?, session_data = ?, world_state = ?
        WHERE id = (SELECT id FROM game_states ORDER BY created_at DESC LIMIT 1)
    """, (plot_progress, json.dumps(session_data), json.dumps(world_state)))
    
    conn.commit()
    conn.close()

# Location Operations
def create_location(name: str, description: str, properties: Optional[Dict] = None) -> int:
    """Create a new location"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO locations (name, description, properties)
        VALUES (?, ?, ?)
    """, (name, description, json.dumps(properties) if properties else None))
    
    location_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return location_id

def get_location(location_id: int):
    """Get location by ID"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM locations WHERE id = ?", (location_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_all_locations():
    """Get all locations"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM locations")
    results = cursor.fetchall()
    conn.close()
    return results

# Entity Operations
def create_entity(name: str, entity_type: str, description: str, location_id: int, properties: Optional[Dict] = None) -> int:
    """Create a new entity"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO entities (name, entity_type, description, location_id, properties)
        VALUES (?, ?, ?, ?, ?)
    """, (name, entity_type, description, location_id, json.dumps(properties) if properties else None))
    
    entity_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entity_id

def get_entities_by_location(location_id: int):
    """Get entities at a specific location"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM entities WHERE location_id = ?", (location_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_entities_by_type(entity_type: str):
    """Get entities by type"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM entities WHERE entity_type = ?", (entity_type,))
    results = cursor.fetchall()
    conn.close()
    return results

# Episodic Memory Operations
def add_episodic_memory(content: str, metadata: Optional[Dict] = None):
    """Add content to episodic memory"""
    try:
        client = get_chromadb_client()
        collection = client.get_collection("episodic_memory")
        
        # Generate a simple ID
        import uuid
        memory_id = str(uuid.uuid4())
        
        # Add to collection
        collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[memory_id]
        )
    except Exception as e:
        print(f"Error adding episodic memory: {e}")

def search_episodic_memory(query: str, n_results: int = 5):
    """Search episodic memory"""
    try:
        client = get_chromadb_client()
        collection = client.get_collection("episodic_memory")
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results
    except Exception as e:
        print(f"Error searching episodic memory: {e}")
        return {"documents": [], "metadatas": []} 