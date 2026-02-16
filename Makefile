.PHONY: run install lint format clean install-model

run:
	uv run main.py

install:
	uv sync

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	rm -rf __pycache__ .ruff_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

install-model:
	ollama create lfm2.5-thinking:1.2b-32k -f models/lfm2.5-thinking.modelfile
	ollama rm lfm2.5-thinking:1.2b