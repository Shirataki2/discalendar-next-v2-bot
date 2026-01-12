#!/bin/bash
# Lint and type check Python code

set -e

echo "Running Ruff linter..."
uv run ruff check src tests

echo "Running MyPy type checker..."
uv run mypy src

echo "Linting complete!"
