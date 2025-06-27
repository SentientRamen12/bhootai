import json
from typing import List, Dict, Any, Optional
from collections import deque
from datetime import datetime
import sqlite3

from llm import LLM
from models import Conversation, Interaction
from database_setup import DatabaseManager


class World:
    def __init__(self, world_prompt_file: str = "world_prompt.txt", db_manager: Optional[DatabaseManager] = None):
        """
        Initialize the World class.
        
        Args:
            world_prompt_file (str): Path to the world prompt file
            db_manager (DatabaseManager): Database manager instance
        """
        # Load world prompt
        self.world_prompt = self._load_world_prompt(world_prompt_file)
        
        # Initialize database manager
        self.db_manager = db_manager or DatabaseManager()
        
        # Initialize LLM
        self.llm = LLM()
        
        # Message management
        self.messages = deque(maxlen=10)  # Running list of messages (max 10)
        self.message_stack = deque(maxlen=10)  # Stack for popped messages
        
        # Summary system prompt for vector search
        self.summary_prompt = """You are a helpful assistant that creates very short summaries of conversation context for search purposes. 
        Create a brief, concise summary (2-3 sentences maximum) that captures the key points and context of the conversation. 
        Focus on the most recent and relevant information that would be useful for finding related world context."""
    
    def _load_world_prompt(self, prompt_file: str) -> str:
        """Load the world prompt from file."""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            # Default world prompt if file doesn't exist
            return """You are the narrator and controller of a supernatural world. 
            You respond to players in character, describing the world around them and their interactions with it.
            Always respond with a JSON object containing:
            - "response_text": Your narrative response to the player
            - "interaction_description": A brief description of what happened for the database
            
            Keep responses engaging and atmospheric, drawing from the world context provided."""
    
    def process_user_message(self, user_message: str, user_id: str = "player") -> str:
        """
        Process a user message through the world system.
        
        Args:
            user_message (str): The user's message
            user_id (str): The user's identifier
            
        Returns:
            str: The world's response text
        """
        # Get last 10 interactions from database
        conn = self.db_manager.get_sqlite_connection()
        recent_interactions = Interaction.get_recent_interactions(conn, limit=10)
        conn.close()
        
        # Check if this is the first message (no previous interactions)
        is_first_message = len(recent_interactions) == 0
        
        if is_first_message:
            # Use initial world context for the first message
            world_context = self._get_initial_world_context()
        else:
            # Create context for summary
            context_messages = []
            for interaction in recent_interactions:
                context_messages.append({
                    "role": "user" if interaction.entity == user_id else "assistant",
                    "content": interaction.description
                })
            
            # Add current message
            context_messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Get short summary for vector search
            summary_messages = [
                {"role": "system", "content": self.summary_prompt},
                {"role": "user", "content": f"Summarize this conversation context:\n{json.dumps(context_messages, indent=2)}"}
            ]
            
            try:
                summary = self.llm.llm_call(summary_messages)
            except Exception as e:
                print(f"Error generating summary: {e}")
                summary = user_message  # Fallback to user message
            
            # Vector search for relevant world context
            try:
                search_results = self.db_manager.search_world_context(summary, n_results=5)
                world_context = self._format_search_results(search_results)
            except Exception as e:
                print(f"Error in vector search: {e}")
                world_context = "No relevant world context found."
        
        # Prepare full context for LLM
        full_context = self._prepare_full_context(user_message, world_context, recent_interactions)
        
        # Get LLM response
        try:
            response = self.llm.llm_call(full_context)
            response_data = self._parse_llm_response(response)
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            response_data = {
                "response_text": "The world seems to be in a state of flux. Try again.",
                "interaction_description": f"User said: {user_message}"
            }
        
        # Save interaction to database
        interaction = Interaction(
            entity=user_id,
            description=response_data["interaction_description"]
        )
        conn = self.db_manager.get_sqlite_connection()
        interaction.save(conn)
        conn.close()
        
        # Add message to running list
        message_entry = {
            "timestamp": datetime.now(),
            "user_message": user_message,
            "world_response": response_data["response_text"],
            "interaction_description": response_data["interaction_description"]
        }
        
        # Check if we need to pop a message
        if len(self.messages) >= 10:
            popped_message = self.messages.popleft()
            self.message_stack.append(popped_message)
            
            # Check if stack is full and summarize
            if len(self.message_stack) >= 10:
                self._summarize_and_refresh_stack()
        
        self.messages.append(message_entry)
        
        return response_data["response_text"]
    
    def _get_initial_world_context(self) -> str:
        """Get the initial world context from file."""
        try:
            with open("initial_world_context.txt", 'r', encoding='utf-8') as f:
                initial_context = f.read().strip()
            
            if initial_context:
                return f"Initial World Context:\n\n{initial_context}\n\nThis is your first interaction with this world. Use this context to establish the setting and atmosphere."
            else:
                return "Welcome to a mysterious world. This is your first interaction here."
        except FileNotFoundError:
            return "Welcome to a mysterious world. This is your first interaction here."
        except Exception as e:
            print(f"Error reading initial world context: {e}")
            return "Welcome to a mysterious world. This is your first interaction here."
    
    def _format_search_results(self, search_results: Dict[str, Any]) -> str:
        """Format vector search results into readable text."""
        if not search_results or not search_results.get('documents'):
            return "No relevant world context found."
        
        formatted_context = "Relevant world context:\n\n"
        documents = search_results['documents'][0]  # First query results
        metadatas = search_results['metadatas'][0]
        
        for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
            formatted_context += f"Context {i+1}:\n{doc}\n\n"
        
        return formatted_context
    
    def _prepare_full_context(self, user_message: str, world_context: str, recent_interactions: List[Interaction]) -> List[Dict[str, str]]:
        """Prepare the full context for the LLM."""
        messages = [
            {"role": "system", "content": self.world_prompt},
            {"role": "user", "content": f"World Context:\n{world_context}\n\nRecent Interactions:\n{self._format_recent_interactions(recent_interactions)}\n\nUser Message: {user_message}\n\nPlease respond with a JSON object containing 'response_text' and 'interaction_description'."}
        ]
        return messages
    
    def _format_recent_interactions(self, interactions: List[Interaction]) -> str:
        """Format recent interactions for context."""
        if not interactions:
            return "No recent interactions."
        
        formatted = ""
        for interaction in interactions[-5:]:  # Last 5 interactions
            formatted += f"- {interaction.entity}: {interaction.description}\n"
        return formatted
    
    def _parse_llm_response(self, response: str) -> Dict[str, str]:
        """Parse the LLM response to extract JSON."""
        try:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                parsed = json.loads(json_str)
                return {
                    "response_text": parsed.get("response_text", response),
                    "interaction_description": parsed.get("interaction_description", "Interaction occurred")
                }
            else:
                # Fallback if no JSON found
                return {
                    "response_text": response,
                    "interaction_description": "User interaction with the world"
                }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "response_text": response,
                "interaction_description": "User interaction with the world"
            }
    
    def _summarize_and_refresh_stack(self):
        """Summarize messages in the stack and add to world context."""
        if not self.message_stack:
            return
        
        # Create summary of stack messages
        summary_content = "Summary of recent interactions:\n\n"
        for msg in self.message_stack:
            summary_content += f"- {msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}: {msg['interaction_description']}\n"
        
        # Add to world context in vector database
        summary_id = f"interaction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metadata = {
            "type": "interaction_summary",
            "category": "player_interactions",
            "timestamp": datetime.now().isoformat(),
            "message_count": len(self.message_stack)
        }
        
        try:
            self.db_manager.add_world_context(summary_content, summary_id, metadata)
            print(f"Added interaction summary to world context: {summary_id}")
        except Exception as e:
            print(f"Error adding summary to world context: {e}")
        
        # Clear the stack
        self.message_stack.clear()
    
    def get_message_history(self) -> List[Dict[str, Any]]:
        """Get the current message history."""
        return list(self.messages)
    
    def get_stack_status(self) -> Dict[str, Any]:
        """Get the status of the message stack."""
        return {
            "stack_size": len(self.message_stack),
            "messages_in_stack": list(self.message_stack),
            "is_full": len(self.message_stack) >= 10
        }
    
    def get_initial_welcome_message(self) -> str:
        """
        Generate an initial welcome message from the world.
        
        Returns:
            str: The world's initial welcome message
        """
        # Get initial world context
        world_context = self._get_initial_world_context()
        
        # Create a special prompt for the initial message
        initial_prompt = f"""You are the narrator and controller of a nightmarish horror realm. 

{self.world_prompt}

This is the very first message the player will see when they enter your world. Create a compelling, atmospheric opening that immediately establishes the horror setting and draws them into the nightmare. End with an actionable choice that forces them to make their first decision in this cursed realm.

World Context:
{world_context}

Generate an opening message that welcomes the player to this horror realm and immediately presents them with their first terrifying choice."""

        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": "Generate the initial welcome message for a player entering this horror realm for the first time."}
        ]
        
        try:
            response = self.llm.llm_call(messages)
            response_data = self._parse_llm_response(response)
            return response_data["response_text"]
        except Exception as e:
            print(f"Error generating initial welcome message: {e}")
            # Fallback welcome message
            return """The darkness welcomes you, foolish mortal. You have stumbled into a realm where nightmares take form and sanity is a distant memory. The air itself seems to pulse with malevolent energy, and you can feel the weight of countless eyes watching your every move from the shadows.

Do you investigate the ominous sounds to your left, or approach the flickering light to your right?"""
