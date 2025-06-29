from src.data.database import get_sqlite_connection, get_chromadb_client

def create_sqlite_schema():
    """Create SQLite database schema"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    # Player table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            health INTEGER DEFAULT 100,
            sanity INTEGER DEFAULT 100,
            current_location_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Location table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS location (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            properties TEXT, -- JSON for location-specific properties
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Entity table (single table with types)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entity (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL, -- 'npc', 'creature', 'item', 'object'
            description TEXT,
            location_id INTEGER,
            properties TEXT, -- JSON for entity-specific properties
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES location (id)
        )
    """)
    
    # GameState table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY,
            current_plot_progress TEXT,
            session_data TEXT, -- JSON for session info
            world_state TEXT, -- JSON for overall world state
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def setup_chromadb():
    """Setup ChromaDB collection for episodic memory"""
    client = get_chromadb_client()
    
    # Create or get episodic memory collection
    collection = client.get_or_create_collection(
        name="episodic_memory",
        metadata={"description": "Episodic memories for story context"}
    )
    
    return collection 