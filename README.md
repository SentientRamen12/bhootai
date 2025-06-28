# 🌙 BhootAI - Interactive Horror Text RPG

An AI-powered text-based horror RPG where players navigate a cursed realm with an intelligent Dungeon Master that dynamically generates plot and responds to player actions.

## 🎮 Features

- **Dynamic Storytelling**: AI Dungeon Master generates plot points based on player actions
- **Episodic Memory**: Intelligent context retrieval from conversation history
- **Horror Atmosphere**: Immersive horror-themed narrative with psychological elements
- **Fresh Sessions**: Each session starts with a clean slate
- **Multi-LLM Support**: Works with OpenAI, Anthropic, and Gemini

## 🏗️ Architecture

```
bhootai/
├── src/
│   ├── core/           # Core system components
│   ├── agents/         # AI agents (Dungeon Master)
│   ├── world/          # World state management
│   ├── data/           # Database layer (SQLite + ChromaDB)
│   ├── tools/          # Extensible tools system
│   └── utils/          # Shared utilities (LLM client)
├── data/               # Database files
├── config/             # Configuration
├── prompts/            # System prompts
└── tests/              # Test suite
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file:
```bash
# Choose your LLM provider
LLM_PROVIDER=openai  # or anthropic, gemini

# API Keys (only need the one for your chosen provider)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here

# Optional: Customize models
OPENAI_MODEL=gpt-4
ANTHROPIC_MODEL=claude-3-sonnet-20240229
GEMINI_MODEL=gemini-pro
```

### 3. Run the Game
```bash
python main.py
```

## 🎯 How It Works

### Core Components

1. **World Manager**: 
   - Manages world state and episodic memory
   - Breaks initial context into searchable chunks
   - Provides context to the Dungeon Master

2. **Dungeon Master**:
   - Generates dynamic plot points
   - Responds to player actions with atmospheric descriptions
   - Maintains conversation history and plot coherence

3. **Memory System**:
   - Stores episodic memories after 20 interactions
   - Provides semantic search for relevant context
   - Enables coherent long-term storytelling

### Game Flow

1. **Initialization**: World loads context, DM sets up initial plot
2. **Player Input**: Player describes actions or asks questions
3. **Context Retrieval**: DM gets relevant world context and memory
4. **Response Generation**: DM creates atmospheric, plot-advancing response
5. **Plot Extension**: New plot points generated based on player action
6. **Memory Storage**: Interaction stored for future context
7. **Session Cleanup**: All data cleared for fresh start

## 🔧 Configuration

### Custom Prompts
Modify prompts in the `prompts/` folder:
- `prompts/system/dm_system.txt`: Dungeon Master personality
- `prompts/agents/plot_generator.txt`: Plot generation instructions

### World Context
Replace `initial_world_context.txt` with your own horror setting description.

### Database Settings
Database paths configured in `config/configs.py`:
- SQLite: `data/sqlite/game.db`
- ChromaDB: `data/chromadb/`

## 🎭 Game Commands

- **Normal Input**: Describe your actions, ask questions, explore
- **quit/exit/q**: End the current session
- **Ctrl+C**: Emergency exit

## 🧪 Development

### Project Structure
```
src/
├── agents/dungeon_master/  # DM implementation
├── world/                  # World state management
├── data/                   # Database operations
├── utils/                  # LLM client, utilities
└── core/                   # Core system (future)
```

### Adding Features
- **New Agents**: Extend base agent classes in `src/agents/`
- **Tools**: Add to `src/tools/` for DM capabilities
- **Memory Types**: Extend episodic memory system
- **World Elements**: Add new entity types or location properties

### Testing
```bash
# Run tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
```

## 🔮 Future Enhancements

- **Multiple Agents**: Additional AI agents for NPCs
- **Tool System**: DM can use tools for complex actions
- **Persistent Worlds**: Option to save/load game states
- **Multiplayer**: Multiple players in shared world
- **Voice Interface**: Speech-to-text integration
- **Visual Elements**: ASCII art and formatting

## 📝 License

This project is open source. Feel free to modify and extend for your own horror RPG adventures!

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your chosen provider's API key is set
2. **Import Errors**: Make sure all dependencies are installed
3. **Database Errors**: Check file permissions in `data/` directory
4. **Memory Issues**: ChromaDB requires sufficient disk space

### Debug Mode
Add debug logging by modifying the main game loop or using Python's logging module.

---

**Enter the nightmare realm at your own risk...** 🌙 