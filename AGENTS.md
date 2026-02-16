# AGENTS.md

This document provides guidance for AI coding agents working in this repository.

## Project Overview

This is a Python CLI application that uses LangChain with Ollama to create an AI agent that fetches Pokémon information from the PokéAPI.

## Requirements

- Python >= 3.12
- Ollama (running locally with models available)

## Build/Lint/Test Commands

### Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
# Or with uv:
uv sync
```

### Running the Application

```bash
python main.py
```

### Linting and Type Checking

```bash
# If using ruff (recommended)
ruff check .
ruff format . --check

# If using mypy for type checking
mypy .
```

### Testing

```bash
# Run all tests (if tests exist)
pytest

# Run a single test file
pytest tests/test_example.py

# Run a single test function
pytest tests/test_example.py::test_function_name

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=.
```

## Code Style Guidelines

### Imports

Group imports in the following order, separated by blank lines:

1. Third-party library imports (langchain, requests, etc.)
2. Standard library imports
3. Local application imports

Example:
```python
from langchain_ollama import ChatOllama
from langchain.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from langchain.tools import tool
from langchain.agents import create_agent

import requests
```

### Formatting

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use double quotes for strings
- Use f-strings for string formatting
- Use trailing commas in multi-line collections

### Naming Conventions

- Functions: `snake_case` (e.g., `fetch_pokemon`, `fetch_pokemon_ability`)
- Variables: `snake_case` (e.g., `pokemon_name`, `ability_list`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- Type parameters: `PascalCase` (e.g., `T`, `TModel`)

### Type Hints

- Always use type hints for function parameters
- Use type hints for return types
- Use `Optional[T]` for optional parameters
- Use `list[T]`, `dict[K, V]` instead of `List[T]`, `Dict[K, V]` (Python 3.12+)

Example:
```python
def fetch_pokemon(pokemon_name: str) -> str:
    ...

def fetch_pokemon_ability(ability_name: str) -> str:
    ...
```

### Docstrings

Use Google-style docstrings for public functions:

```python
def fetch_pokemon(pokemon_name: str) -> str:
    """Fetch general information about a Pokémon, including its abilities.

    Args:
        pokemon_name (str): the name of the Pokémon in lowercase.
    """
```

### Error Handling

- Return descriptive error strings for expected failures (API errors, not found, etc.)
- Let exceptions propagate for unexpected failures
- Check HTTP status codes and return meaningful error messages

Example:
```python
r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/")
if r.status_code != 200:
    return f"Error fetching pokémon {pokemon_name}: HTTP status code {r.status_code}"
```

### Code Comments

- DO NOT add comments unless asked by the user
- Let the code be self-documenting through clear naming and structure

### Functions

- Keep functions small and focused
- Use list comprehensions for simple transformations
- Return early for error conditions

### Decorators

Use the `@tool` decorator from langchain for functions that should be available as agent tools:

```python
@tool
def fetch_pokemon(pokemon_name: str) -> str:
    """Fetch general information about a Pokémon."""
    ...
```

## Project Structure

```
ask-ollama/
├── main.py           # Main application entry point
├── pyproject.toml    # Project configuration and dependencies
├── README.md         # Project documentation
└── AGENTS.md         # This file
```

## Dependencies

- `langchain[ollama]` - LangChain framework with Ollama integration
- `ollama` - Ollama Python client
- `requests` - HTTP client for API calls (transitive dependency)

## Key Patterns

### Tool Functions

Tool functions called by the AI agent should:
1. Use the `@tool` decorator
2. Have a clear docstring describing what the tool does
3. Accept string parameters from the AI
4. Return a string response for the AI to process

### API Integration

When working with APIs:
1. Use GET requests via `requests` library
2. Check status codes before processing
3. Extract relevant data from JSON responses
4. Handle missing/optional fields gracefully

## Notes

- The application is designed for CLI usage with Portuguese language prompts
- The agent uses a local Ollama model (configure model name in `main.py`)
- System prompts instruct the AI to be concise and provide code when possible