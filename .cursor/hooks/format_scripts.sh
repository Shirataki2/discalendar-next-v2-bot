#!/bin/bash
# Format Python code using Ruff

set -e

echo "Formatting code with Ruff..."
uv run ruff format src tests

echo "Formatting complete!"
