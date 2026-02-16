# Ask Ollama

A Python CLI application that uses LangChain with Ollama to create an AI agent that fetches Pokémon information from the PokéAPI.

## Prerequisites

- Python >= 3.12
- [Ollama](https://ollama.ai/) installed and running locally
- A compatible model pulled (e.g., `ollama pull lfm2.5-thinking:1.2b-32k`)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd ask-ollama

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
# Or with uv:
uv sync
```

## Usage

```bash
python main.py
```

The agent will automatically query information about Pokémon and their relationships. You can modify the question in `main.py` to ask different questions.

## How It Works

The application creates a LangChain agent with:

1. **A tool function** (`fetch_pokemon`) that retrieves Pokémon data from the PokéAPI, including:
   - Basic Pokémon info (name, abilities, stats, moves)
   - Ability details (name, effect)
   - Move details (accuracy, power, type, damage class)
   - Stat details (affecting moves and natures)

2. **A ChatOllama model** configured with:
   - Configurable model selection (see `main.py`)
   - Temperature: 0.7
   - Context window: 32768 tokens

3. **A system prompt** (in Portuguese) instructing the AI to be concise and code-focused.

## Configuration

Edit `main.py` to:

- Change the Ollama model (uncomment the desired model line)
- Adjust temperature and other model parameters
- Modify the system prompt
- Change the initial query

## Project Structure

```
ask-ollama/
├── main.py           # Main application entry point
├── pyproject.toml    # Project configuration and dependencies
├── README.md         # This file
└── AGENTS.md         # AI agent guidelines
```

## API Reference

The application consumes the [PokéAPI](https://pokeapi.io/) to fetch:

- `/pokemon/{name}` - Pokémon details
- `/ability/{name}` - Ability information
- `/move/{name}` - Move information
- `/stat/{name}` - Stat information

## License

MIT License. See [LICENSE.txt](LICENSE.txt) for more details.