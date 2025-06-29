#!/usr/bin/env python3
"""
BhootAI - Interactive Horror Text RPG
Main game loop that manages player-DM interactions
"""

import sys
import os
from pathlib import Path

# Suppress HuggingFace tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.world.world import World
from src.agents.dungeon_master.dm import DungeonMaster
from src.db.database import get_sqlite_connection, get_chromadb_client
from src.db.crud import get_current_game_state
from src.utils.terminal_ui import TerminalUI

def clear_databases():
    """Clear all data from databases for fresh session"""
    print("Clearing databases for fresh session...")
    
    # Clear SQLite database
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    # Clear all tables
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':  # Skip SQLite internal table
            cursor.execute(f"DELETE FROM {table_name}")
    
    conn.commit()
    conn.close()
    
    # Clear ChromaDB collection
    try:
        client = get_chromadb_client()
        collection = client.get_collection("episodic_memory")
        
        # Get all documents to delete them by ID
        results = collection.get()
        if results and results.get('ids'):
            collection.delete(ids=results['ids'])
            
    except Exception as e:
        pass  # Silently handle ChromaDB errors

def log_to_file(message: str):
    """Log messages to logs.txt file"""
    try:
        with open("logs.txt", "a") as f:
            f.write(f"{message}\n")
    except:
        pass  # Silently fail if logging fails

def main():
    """Main game loop"""
    ui = TerminalUI()
    
    try:
        # Show loading screen
        ui.show_loading_screen()
        
        # Clear databases for fresh session
        clear_databases()
        
        # Show title screen
        ui.show_title_screen()
        
        # Get player name
        player_name = ui.get_player_name()
        
        # Initialize world and DM
        print("Initializing the cursed realm...")
        world = World()
        dm = DungeonMaster(world)
        
        # Generate chapter description
        chapter_description = dm.generate_opening_scene()
        
        # Show chapter header
        ui.show_chapter_header(1, "THE AWAKENING", chapter_description)
        
        # Wait for player to say "start"
        while True:
            player_input = input(f"{player_name}: ").strip().lower()
            if player_input == "start":
                break
            elif player_input in ['quit', 'exit', 'q']:
                return
            else:
                print("Say 'start' to begin your nightmare...")
        
        # Generate first DM interaction automatically
        first_interaction = dm.respond_to_player("begin")
        ui.show_dm_response(first_interaction)
        
        # Game loop
        interaction_count = 1  # Start at 1 since we already had the first interaction
        while True:
            try:
                # Get player input
                player_input = input(f"{player_name}: ").strip()
                
                # Check for exit commands
                if player_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not player_input:
                    print("Please say something...")
                    continue
                
                # Get DM response
                response = dm.respond_to_player(player_input)
                ui.show_dm_response(response)
                
                interaction_count += 1
                
                # Show progress every 10 interactions
                if interaction_count % 10 == 0:
                    plot_status = dm.get_current_plot_status()
                    ui.show_progress(interaction_count, plot_status)
                
            except KeyboardInterrupt:
                print(f"\n\n{player_name}, you are torn from the nightmare realm...")
                break
            except Exception as e:
                log_to_file(f"Error in game loop: {e}")
                ui.show_error_message(str(e))
                continue
        
        # Show exit screen
        plot_status = dm.get_current_plot_status()
        ui.show_exit_screen(player_name, interaction_count, plot_status)
        
    except Exception as e:
        log_to_file(f"Fatal error: {e}")
        ui.show_error_message(str(e))
        sys.exit(1)
    
    finally:
        # Clean up databases
        print("Cleaning up session data...")
        clear_databases()
        print("Session cleanup complete.")

if __name__ == "__main__":
    main()
