import sqlite3
import json
from pathlib import Path
from typing import Optional
import chromadb
from config.configs import SQLITE_DB_PATH, CHROMADB_PATH

def get_sqlite_connection():
    """Get SQLite database connection"""
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(SQLITE_DB_PATH))

def get_chromadb_client():
    """Get ChromaDB client"""
    CHROMADB_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMADB_PATH))

def create_sqlite_schema():
    """Create SQLite database schema"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plot_progress TEXT,
            session_data TEXT,
            world_state TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            properties TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            description TEXT,
            location_id INTEGER,
            properties TEXT,
            FOREIGN KEY (location_id) REFERENCES locations (id)
        )
    """)
    
    conn.commit()
    conn.close()

def setup_chromadb():
    """Setup ChromaDB collection"""
    client = get_chromadb_client()
    
    # Get or create collection
    try:
        collection = client.get_collection("episodic_memory")
    except:
        collection = client.create_collection("episodic_memory")
    
    return collection 