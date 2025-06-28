import json
from typing import List, Dict, Optional, Any
from pathlib import Path
from src.utils.llm import LLMClient
from src.world.world import World
from config.configs import BASE_DIR

class DungeonMaster:
    def __init__(self, world: World, system_prompt_path: Optional[str] = None):
        """Initialize the Dungeon Master with world and system prompt"""
        self.world = world
        self.llm_client = LLMClient()
        
        # Load system prompt from file
        system_prompt_path = system_prompt_path or str(BASE_DIR / "prompts" / "system" / "dm_system.txt")
        self.system_prompt = self._load_prompt(system_prompt_path)
        
        # Load opening scene prompt
        opening_prompt_path = str(BASE_DIR / "prompts" / "system" / "opening_scene.txt")
        self.opening_scene_prompt = self._load_prompt(opening_prompt_path)
        
        # Load plot generator prompt
        plot_prompt_path = str(BASE_DIR / "prompts" / "agents" / "plot_generator.txt")
        self.plot_generator_prompt = self._load_prompt(plot_prompt_path)

        # Plot management
        self.plot_points = []
        self.current_plot_index = 0
        self.conversation_history = []
        
        # Initialize the scenario
        self._setup_initial_scenario()
    
    def _load_prompt(self, prompt_path: str) -> str:
        """Load prompt from file"""
        try:
            with open(prompt_path, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"Warning: Prompt file not found at {prompt_path}")
            return ""
        except Exception as e:
            print(f"Error loading prompt from {prompt_path}: {e}")
            return ""
    
    def _setup_initial_scenario(self):
        """Set up the initial plot and scenario"""
        initial_plot = [
            "Player awakens in a mysterious, cursed location",
            "Discover the nature of the horror realm",
            "Encounter first supernatural entity or phenomenon",
            "Find a way to navigate the dangerous environment",
            "Uncover clues about the curse or dark forces at work"
        ]
        
        self.plot_points = initial_plot
        self.current_plot_index = 0
        
        # Store initial plot in world state
        self.world.update_world_state(
            plot_progress="initial_setup",
            world_state={"plot_points": initial_plot, "current_index": 0}
        )
    
    def _update_plot_progression(self, player_action: str):
        """Update plot progression based on player action"""
        current_situation = f"Plot point {self.current_plot_index + 1}: {self.plot_points[self.current_plot_index]}"
        
        # Store the completed plot point as episodic memory
        if self.current_plot_index < len(self.plot_points):
            completed_plot = self.plot_points[self.current_plot_index]
            self.world.add_episodic_memory_from_messages([
                {"role": "system", "content": f"Completed plot point: {completed_plot}"},
                {"role": "user", "content": player_action},
                {"role": "assistant", "content": f"Plot point '{completed_plot}' completed through action: {player_action}"}
            ])
        
        # Generate new plot points based on current situation and player action
        new_points = self._generate_plot_extension(current_situation, player_action)
        
        # Update plot points - replace completed ones and add new ones
        if self.current_plot_index < len(self.plot_points):
            # Remove the completed plot point
            self.plot_points.pop(self.current_plot_index)
        
        # Add new plot points at the current position
        for i, point in enumerate(new_points):
            self.plot_points.insert(self.current_plot_index + i, point)
        
        # Move to next plot point (or stay at current if no new points were added)
        if new_points:
            self.current_plot_index += 1
        
        # Update world state
        self.world.update_world_state(
            plot_progress=f"plot_point_{self.current_plot_index}",
            world_state={
                "plot_points": self.plot_points,
                "current_index": self.current_plot_index,
                "last_action": player_action,
                "completed_plots": self._get_completed_plot_summary()
            }
        )
    
    def _get_completed_plot_summary(self) -> str:
        """Get a summary of completed plot points for episodic memory"""
        # This would track completed plot points across sessions
        # For now, return current progress
        return f"Completed {self.current_plot_index} plot points"
    
    def _generate_plot_extension(self, current_situation: str, player_action: str) -> List[str]:
        """Generate new plot points based on current situation and player action"""
        # Get episodic context for plot generation
        episodic_context = self.world.get_episodic_context(f"{current_situation} {player_action}", n_results=3)
        
        # Get current world state for context
        world_state = self.world.get_current_world_state()
        
        prompt = f"""Current situation: {current_situation}
Player action: {player_action}
Current plot points: {self.plot_points}
World state: {world_state.get('world_state', {})}

Episodic memory context: {episodic_context}

Based on the player's action and current situation, generate 2-3 new plot points that are:
1. Relevant to what just happened
2. Build upon the current story
3. Provide clear direction for the horror narrative

Generate as a simple list, one per line:"""

        response = self.llm_client.generate(
            system_prompt=self.plot_generator_prompt,
            prompt=prompt,
            temperature=0.8
        )
        
        # Parse response into plot points
        new_points = [point.strip() for point in response.split('\n') if point.strip()]
        return new_points[:3]  # Limit to 3 new points
    
    def _get_relevant_context(self, player_input: str) -> str:
        """Get relevant world context for the current situation"""
        # Get world context based on player input
        context_results = self.world.get_world_context(player_input, n_results=3)
        
        # Get episodic context
        episodic_context = self.world.get_episodic_context(player_input, n_results=2)
        
        # Get current world state
        world_state = self.world.get_current_world_state()
        
        # Get current location info if available
        location_context = ""
        if world_state.get("session_data", {}).get("current_location_id"):
            location_id = world_state["session_data"]["current_location_id"]
            location_info = self.world.get_location_info(location_id)
            if location_info:
                location_context = f"Current location: {location_info['location'][1]} - {location_info['location'][2]}"
        
        # Combine context
        context_parts = []
        if context_results.get("documents"):
            context_parts.extend(context_results["documents"])
        if episodic_context and episodic_context != "No relevant episodic memory found":
            context_parts.append(f"Episodic context: {episodic_context}")
        if location_context:
            context_parts.append(location_context)
        if world_state.get("plot_progress"):
            context_parts.append(f"Plot progress: {world_state['plot_progress']}")
        
        return " | ".join(context_parts) if context_parts else "No specific context available"
    
    def generate_opening_scene(self) -> str:
        """Generate the initial opening scene for the player"""
        context = self._get_relevant_context("castle entrance horror awakening")
        
        opening_prompt = f"""Context: {context}

Create a brief, atmospheric opening scene for a horror RPG set in Dracula's castle. Keep it concise (2-3 sentences maximum).

Focus on the immediate surroundings and the player's disorientation. End with: Say 'start' to begin your nightmare."""

        response = self.llm_client.generate(
            system_prompt=self.opening_scene_prompt,
            prompt=opening_prompt,
            temperature=0.8
        )
        
        return response
    
    def respond_to_player(self, player_input: str) -> str:
        """Generate response to player input with selective options"""
        # Get relevant context
        context = self._get_relevant_context(player_input)
        
        # Build conversation history for context
        messages = self.conversation_history[-10:]  # Last 10 messages for context
        
        # Create simple prompt that relies on the system prompt
        response_prompt = f"""Context: {context}

Current plot point: {self.plot_points[self.current_plot_index] if self.current_plot_index < len(self.plot_points) else "Plot complete"}

Player says: {player_input}"""

        # Generate response
        response = self.llm_client.generate(
            system_prompt=self.system_prompt,
            messages=messages,
            prompt=response_prompt,
            temperature=0.8
        )
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": player_input})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Store in episodic memory (will only store after threshold)
        self.world.add_episodic_memory_from_messages([
            {"role": "user", "content": player_input},
            {"role": "assistant", "content": response}
        ])
        
        # Update plot progression
        self._update_plot_progression(player_input)
        
        return response
    
    def get_current_plot_status(self) -> Dict[str, Any]:
        """Get current plot status and upcoming points"""
        return {
            "current_index": self.current_plot_index,
            "current_point": self.plot_points[self.current_plot_index] if self.current_plot_index < len(self.plot_points) else "Complete",
            "upcoming_points": self.plot_points[self.current_plot_index + 1:self.current_plot_index + 4],
            "total_points": len(self.plot_points),
            "completed_points": self.current_plot_index,
            "plot_progress": f"{self.current_plot_index}/{len(self.plot_points)}"
        }
    
    def get_plot_summary(self) -> str:
        """Get a summary of the current plot progression"""
        status = self.get_current_plot_status()
        return f"""Plot Progress: {status['plot_progress']} points completed
Current: {status['current_point']}
Upcoming: {', '.join(status['upcoming_points'])}"""
    
    def get_completed_plot_points(self) -> List[str]:
        """Get a list of completed plot points for episodic memory"""
        # This would ideally track across sessions, but for now return current progress
        world_state = self.world.get_current_world_state()
        return world_state.get('world_state', {}).get('completed_plots', []) 