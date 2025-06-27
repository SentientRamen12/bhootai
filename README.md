# bhootai

A text-based adventure game built with Python featuring an intelligent world system with vector search and LLM integration.

## Features

- **Intelligent World System**: The World class manages game state with message history and vector search
- **Vector Database Integration**: Uses ChromaDB for semantic search of world context
- **LLM Integration**: Powered by Google's Gemini 2.5 Pro for dynamic responses
- **Message Management**: Maintains a sliding window of recent interactions with automatic summarization
- **Persistent Storage**: SQLite database for conversations and interactions

## Architecture

### World Class
The core `World` class implements the following workflow:

1. **Message Processing**: Takes user input and processes it through the world system
2. **Context Retrieval**: Gets the last 10 interactions from the database
3. **Summary Generation**: Creates a short summary for vector search using LLM
4. **Vector Search**: Searches the vector database for relevant world context (top 5 results)
5. **Response Generation**: Combines context with user message and generates response using LLM
6. **Data Storage**: Saves interactions to database and maintains message history
7. **Memory Management**: Automatically summarizes old messages when stack is full

### Key Components

- **Message History**: Running list of 10 most recent messages
- **Message Stack**: Temporary storage for popped messages (max 10)
- **Automatic Summarization**: When stack is full, messages are summarized and added to world context
- **Vector Search**: Semantic search through world context using ChromaDB
- **LLM Integration**: Dual LLM usage for summarization and response generation

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Google API key for Gemini

### Installation

1. Clone the repository:
```bash
git clone https://github.com/SentientRamen12/bhootai.git
cd bhootai
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
   - On Windows:
   ```bash
   .venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Configuration

1. Create a `.env` file in the root directory:
```bash
touch .env
```

2. Add the following environment variables to your `.env` file:
```env
GOOGLE_API_KEY=your-google-api-key-here
```

**Note:** The system will also accept `GOOGLE_API` or `GEMINI_API_KEY` as alternative environment variable names. Replace the placeholder values with your actual configuration. Variables starting with `#` are commented out and optional.

### Running the Game

Start the game by running:
```bash
python main.py
```

### Testing the World System

Run the test script to see the World class in action:
```bash
python test_world.py
```

## Usage Examples

### Basic World Usage

```python
from world import World
from database_setup import initialize_databases

# Initialize databases
db_manager = initialize_databases()

# Create world instance
world = World(db_manager=db_manager)

# Process user message
response = world.process_user_message("I want to explore the forest")
print(response)

# Get message history
history = world.get_message_history()
print(f"Message history: {len(history)} messages")

# Get stack status
status = world.get_stack_status()
print(f"Stack size: {status['stack_size']}")
```

### Custom World Prompt

You can customize the world behavior by editing `world_prompt.txt`:

```txt
You are the narrator of a cyberpunk world...
```

## File Structure

```
bhootai/
├── world.py              # Main World class implementation
├── llm.py               # LLM integration with Gemini
├── models.py            # Database models (Conversation, Interaction)
├── database_setup.py    # Database initialization and management
├── main.py              # Main game entry point
├── test_world.py        # Test script for World class
├── world_prompt.txt     # System prompt for the world
├── initial_world_context.txt  # Initial world context for vector DB
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
