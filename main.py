'''
Starts the whole game and manages the player interactions
'''

from dotenv import load_dotenv
import os
from database_setup import initialize_databases

load_dotenv()

def main():
    """Main game initialization and entry point"""
    print("Initializing BhootAI game...")
    
    # Initialize databases
    db_manager = initialize_databases()
    
    # TODO: Add game logic here
    print("Game initialized successfully!")
    print("Databases are ready for use.")

if __name__ == "__main__":
    main()





