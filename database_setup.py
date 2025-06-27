'''
Database setup and management for ChromaDB (vector database) and SQLite
'''

import sqlite3
import chromadb
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_dir="data"):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(exist_ok=True)
        
        # SQLite database path
        self.sqlite_path = self.db_dir / "game.db"
        
        # ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=str(self.db_dir / "chroma_db"))
        
    def setup_sqlite(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        conn.close()
        print(f"SQLite database initialized at: {self.sqlite_path}")
    
    def setup_chromadb(self):
        """Initialize ChromaDB client"""
        try:
            print("ChromaDB client initialized successfully")
        except Exception as e:
            print(f"Error setting up ChromaDB: {e}")
    
    def get_sqlite_connection(self):
        """Get a connection to the SQLite database"""
        return sqlite3.connect(self.sqlite_path)
    
    def get_chroma_client(self):
        """Get the ChromaDB client"""
        return self.chroma_client

def initialize_databases():
    """Initialize both databases"""
    db_manager = DatabaseManager()
    
    # Setup SQLite
    db_manager.setup_sqlite()
    
    # Setup ChromaDB
    db_manager.setup_chromadb()
    
    return db_manager

if __name__ == "__main__":
    # Initialize databases when run directly
    db_manager = initialize_databases()
    print("Database setup complete!") 