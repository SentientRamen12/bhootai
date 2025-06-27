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
        """Initialize SQLite database with tables"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        # Create Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create Interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity TEXT NOT NULL,
                description TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"SQLite database initialized with tables at: {self.sqlite_path}")
    
    def setup_chromadb(self):
        """Initialize ChromaDB client with world context collection"""
        try:
            # Create or get the world context collection
            self.world_context_collection = self.chroma_client.get_or_create_collection(
                name="world_context",
                metadata={"description": "World context and lore for the game"}
            )
            
            # Initialize with basic world context if collection is empty
            if self.world_context_collection.count() == 0:
                self.initialize_world_context()
            
            print("ChromaDB client initialized successfully with world context collection")
        except Exception as e:
            print(f"Error setting up ChromaDB: {e}")
    
    def initialize_world_context(self):
        """Initialize the world context with sliding window chunks"""
        # Read world context from file if it exists
        world_context_file = Path("initial_world_context.txt")
        if world_context_file.exists() and world_context_file.stat().st_size > 0:
            with open(world_context_file, 'r', encoding='utf-8') as f:
                full_context = f.read().strip()
        else:
            # Default world context if file is empty or doesn't exist
            full_context = """
            In the depths of an ancient forest, where shadows dance between towering trees and whispers echo through the mist, lies a world untouched by time. This supernatural realm is home to entities both benevolent and malevolent, each carrying secrets of ages past. The air itself seems alive with magic, and every step taken reveals new mysteries waiting to be uncovered. Ancient ruins dot the landscape, their weathered stones telling stories of civilizations long forgotten. The player, a brave explorer drawn by curiosity and perhaps destiny, must navigate this treacherous yet beautiful world. They will encounter spirits that guard ancient knowledge, creatures that test their courage, and artifacts that hold the power to change everything. The world responds to their presence, shifting and adapting as they explore deeper into its heart. Every interaction leaves a mark, every choice ripples through the fabric of this mystical realm. The player's journey is not just about discovery, but about understanding their place in a world where the line between reality and the supernatural blurs into nothingness.
            """
        
        # Create sliding window chunks of 50 words with overlap
        chunks = self.create_sliding_window_chunks(full_context, window_size=50, overlap=10)
        
        # Add chunks to the collection
        for i, chunk in enumerate(chunks):
            chunk_id = f"world_context_chunk_{i:04d}"
            metadata = {
                "type": "world_context",
                "category": "lore",
                "chunk_index": i,
                "total_chunks": len(chunks),
                "word_count": len(chunk.split())
            }
            
            self.world_context_collection.add(
                documents=[chunk],
                metadatas=[metadata],
                ids=[chunk_id]
            )
        
        print(f"World context initialized with {len(chunks)} sliding window chunks")
    
    def create_sliding_window_chunks(self, text: str, window_size: int = 50, overlap: int = 10) -> list:
        """Create sliding window chunks from text"""
        words = text.split()
        chunks = []
        
        if len(words) <= window_size:
            # If text is shorter than window size, return the whole text
            chunks.append(text)
        else:
            # Create sliding window chunks
            step = window_size - overlap
            for i in range(0, len(words) - window_size + 1, step):
                chunk_words = words[i:i + window_size]
                chunk_text = ' '.join(chunk_words)
                chunks.append(chunk_text)
            
            # Add the last chunk if it doesn't overlap completely
            if len(words) > window_size:
                last_chunk_words = words[-window_size:]
                last_chunk_text = ' '.join(last_chunk_words)
                if last_chunk_text not in chunks:
                    chunks.append(last_chunk_text)
        
        return chunks
    
    def add_world_context(self, text: str, context_id: str, metadata: dict = None):
        """Add new world context to the vector database"""
        if metadata is None:
            metadata = {"type": "custom", "category": "lore"}
        
        self.world_context_collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[context_id]
        )
        print(f"Added world context: {context_id}")
    
    def search_world_context(self, query: str, n_results: int = 5):
        """Search world context using semantic similarity"""
        results = self.world_context_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def get_sqlite_connection(self):
        """Get a connection to the SQLite database"""
        return sqlite3.connect(self.sqlite_path)
    
    def get_chroma_client(self):
        """Get the ChromaDB client"""
        return self.chroma_client
    
    def get_world_context_collection(self):
        """Get the world context collection"""
        return self.world_context_collection

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