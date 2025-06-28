import json
import re
from typing import List, Dict, Optional, Any
from pathlib import Path

from src.data.database import get_sqlite_connection, get_chromadb_client
from src.data.schema import create_sqlite_schema, setup_chromadb
from src.data.crud import (
    create_location, get_location, get_all_locations,
    create_entity, get_entities_by_location, get_entities_by_type,
    create_game_state, get_current_game_state, update_game_state,
    add_episodic_memory, search_episodic_memory
)
from config.configs import BASE_DIR

class World:
    def __init__(self, initial_context_path: Optional[str] = None):
        """Initialize the world with context and database connections"""
        self.initial_context_path = initial_context_path or str(BASE_DIR / "initial_world_context.txt")
        
        # Setup databases
        self._setup_databases()
        
        # Initialize world context
        self._initialize_world_context()
        
        # Initialize game state
        self._initialize_game_state()
        
        # Interaction counter for episodic memory
        self.interaction_count = 0
        self.episodic_memory_threshold = 20
    
    def _setup_databases(self):
        """Setup SQLite and ChromaDB connections"""
        # Create SQLite schema
        create_sqlite_schema()
        
        # Setup ChromaDB
        self.chromadb_collection = setup_chromadb()
    
    def _initialize_world_context(self):
        """Load initial world context and break into chunks for vector storage"""
        try:
            with open(self.initial_context_path, 'r') as f:
                context = f.read().strip()
            
            # Break context into 50-word sliding windows
            chunks = self._create_context_chunks(context, window_size=50, overlap=10)
            
            # Store chunks in ChromaDB
            for i, chunk in enumerate(chunks):
                metadata = {
                    "type": "world_context",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "source": "initial_context"
                }
                add_episodic_memory(chunk, metadata)
            
        except FileNotFoundError:
            pass  # Silently handle missing context file
        except Exception as e:
            pass  # Silently handle context loading errors
    
    def _create_context_chunks(self, text: str, window_size: int = 50, overlap: int = 10) -> List[str]:
        """Create sliding window chunks of text"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), window_size - overlap):
            chunk_words = words[i:i + window_size]
            chunk = ' '.join(chunk_words)
            chunks.append(chunk)
            
            if i + window_size >= len(words):
                break
        
        return chunks
    
    def _initialize_game_state(self):
        """Initialize or load existing game state"""
        current_state = get_current_game_state()
        if not current_state:
            create_game_state(
                plot_progress="initial",
                session_data={"session_id": "1", "started": True, "interaction_count": 0},
                world_state={"initialized": True}
            )
    
    def add_episodic_memory_from_messages(self, messages: List[Dict[str, str]], metadata: Optional[Dict] = None):
        """Create episodic memory from conversation messages after threshold"""
        if not messages:
            return
        
        # Increment interaction counter
        self.interaction_count += 1
        
        # Only add to episodic memory after threshold
        if self.interaction_count >= self.episodic_memory_threshold:
            # Combine messages into a single narrative
            narrative = self._messages_to_narrative(messages)
            
            # Add to episodic memory
            memory_metadata = metadata or {}
            memory_metadata.update({
                "type": "conversation",
                "message_count": len(messages),
                "interaction_count": self.interaction_count,
                "timestamp": "current"  # You might want to add actual timestamp
            })
            
            add_episodic_memory(narrative, memory_metadata)
            
            # Reset counter
            self.interaction_count = 0
    
    def _messages_to_narrative(self, messages: List[Dict[str, str]]) -> str:
        """Convert conversation messages to narrative text"""
        narrative_parts = []
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            if role == "user":
                narrative_parts.append(f"Player: {content}")
            elif role == "assistant":
                narrative_parts.append(f"Dungeon Master: {content}")
            else:
                narrative_parts.append(f"{role.title()}: {content}")
        
        return " | ".join(narrative_parts)
    
    def get_world_context(self, query: str, n_results: int = 5) -> Dict:
        """Get relevant world context based on query"""
        results = search_episodic_memory(query, n_results)
        
        # Handle ChromaDB response format properly
        if results.get("documents") and results["documents"]:
            # ChromaDB returns documents as a list of lists
            documents = results["documents"][0] if isinstance(results["documents"], list) else results["documents"]
            metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
            
            return {
                "documents": documents,
                "metadatas": metadatas
            }
        
        return {"documents": [], "metadatas": []}
    
    def get_episodic_context(self, query: str, n_results: int = 3) -> str:
        """Get episodic memory context for plot generation and responses"""
        results = search_episodic_memory(query, n_results)
        
        if results.get("documents") and results["documents"]:
            # ChromaDB returns documents as a list of lists, so we need to flatten
            documents = results["documents"][0] if isinstance(results["documents"], list) else results["documents"]
            metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
            
            context_parts = []
            for i, doc in enumerate(documents):
                if i < len(metadatas):
                    metadata = metadatas[i] or {}
                else:
                    metadata = {}
                context_parts.append(f"Memory {i+1}: {doc}")
            return " | ".join(context_parts)
        
        return "No relevant episodic memory found"
    
    def get_location_info(self, location_id: int) -> Optional[Dict]:
        """Get detailed location information"""
        location = get_location(location_id)
        if not location:
            return None
        
        # Get entities at this location
        entities = get_entities_by_location(location_id)
        
        return {
            "location": location,
            "entities": entities
        }
    
    def get_current_world_state(self) -> Dict:
        """Get current world state"""
        state = get_current_game_state()
        if not state:
            return {}
        
        return {
            "plot_progress": state[1],
            "session_data": json.loads(state[2]) if state[2] else {},
            "world_state": json.loads(state[3]) if state[3] else {}
        }
    
    def update_world_state(self, **kwargs):
        """Update world state"""
        current_state = get_current_game_state()
        if not current_state:
            return
        
        state_id = current_state[0]
        update_game_state(state_id, **kwargs)
    
    def create_location(self, name: str, description: str, properties: Optional[Dict] = None) -> int:
        """Create a new location"""
        return create_location(name, description, properties)
    
    def create_entity(self, name: str, entity_type: str, description: str, location_id: int, properties: Optional[Dict] = None) -> int:
        """Create a new entity"""
        return create_entity(name, entity_type, description, location_id, properties)
    
    def get_entities_by_type(self, entity_type: str) -> List:
        """Get all entities of a specific type"""
        return get_entities_by_type(entity_type)
    
    def get_all_locations(self) -> List:
        """Get all locations"""
        return get_all_locations() 