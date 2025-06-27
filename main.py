'''
Starts the whole game and manages the player interactions
'''

from dotenv import load_dotenv
import os
import sys
from database_setup import initialize_databases
from world import World

load_dotenv()

def check_api_key():
    """Check if Google API key is available"""
    api_key = (
        os.getenv("GOOGLE_API_KEY") or 
        os.getenv("GOOGLE_API") or 
        os.getenv("GEMINI_API_KEY")
    )
    return api_key

def setup_instructions():
    """Display setup instructions"""
    print("\n" + "="*60)
    print("SETUP REQUIRED")
    print("="*60)
    print("To run this game, you need a Google API key for Gemini.")
    print("\n1. Get a Google API key from:")
    print("   https://makersuite.google.com/app/apikey")
    print("\n2. Add it to your .env file:")
    print("   GOOGLE_API_KEY=your-api-key-here")
    print("\n3. Or set it as an environment variable:")
    print("   export GOOGLE_API_KEY=your-api-key-here")
    print("\nAlternative environment variable names:")
    print("   GOOGLE_API or GEMINI_API_KEY")
    print("="*60)

def main():
    """Main game initialization and entry point"""
    print("Initializing BhootAI game...")
    
    # Check for API key
    if not check_api_key():
        setup_instructions()
        sys.exit(1)
    
    try:
        # Initialize databases
        print("Setting up databases...")
        db_manager = initialize_databases()
        
        # Create world instance
        print("Creating world...")
        world = World(db_manager=db_manager)
        
        print("Game initialized successfully!")
        print("Welcome to the horror realm!")
        print("Type 'quit' to exit the game.")
        print("-" * 50)
        
        # Generate and display initial welcome message from the world
        print("\nGenerating your nightmare...")
        try:
            initial_message = world.get_initial_welcome_message()
            print(f"\nWorld: {initial_message}")
        except Exception as e:
            print(f"\nError generating initial message: {e}")
            print("\nWorld: The darkness welcomes you to this cursed realm. Your journey into madness begins now.")
        
        # Game loop
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Farewell, brave explorer. The world will remember your journey.")
                    break
                
                if not user_input:
                    continue
                
                # Process user message through the world
                response = world.process_user_message(user_input)
                print(f"\nWorld: {response}")
                
            except KeyboardInterrupt:
                print("\n\nFarewell, brave explorer. The world will remember your journey.")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                print("The world seems to be in a state of flux. Try again.")
                
    except Exception as e:
        print(f"\nFailed to initialize game: {e}")
        print("Please check your setup and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()





