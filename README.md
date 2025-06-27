# bhootai

A text-based adventure game built with Python.

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

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
# Game Configuration
GAME_NAME=bhootai
DEBUG=false

# Database Configuration (if using a database)
# DATABASE_URL=sqlite:///game.db

# API Keys (if using external services)
# OPENAI_API_KEY=your_openai_api_key_here

# Game Settings
# MAX_PLAYERS=10
# SAVE_GAME_PATH=./saves/
```

**Note:** Replace the placeholder values with your actual configuration. Variables starting with `#` are commented out and optional.

### Running the Game

Start the game by running:
```bash
python main.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
