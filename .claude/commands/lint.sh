#!/bin/bash
# Lint and format Python code

echo "Running code quality checks..."

# Format with black
echo "Formatting with black..."
pipenv run black . 2>/dev/null || echo "Black not installed - run 'pipenv install --dev'"

# Lint with ruff
echo "Linting with ruff..."
pipenv run ruff check . 2>/dev/null || echo "Ruff not installed - run 'pipenv install --dev'"

# Type check with mypy
echo "Type checking with mypy..."
pipenv run mypy . 2>/dev/null || echo "MyPy not installed - run 'pipenv install --dev'"

echo "Code quality checks complete!"