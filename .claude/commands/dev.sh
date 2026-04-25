#!/bin/bash
# Development environment setup

echo "Setting up Python development environment..."

# Check if pipenv is installed
if ! command -v pipenv &> /dev/null; then
    echo "Installing pipenv..."
    pip install pipenv
fi

# Install dependencies
echo "Installing project dependencies..."
pipenv install --dev

# Run initial checks
echo "Running initial checks..."
pipenv run ruff check . 2>/dev/null || echo "Ruff not yet installed"
pipenv run mypy . 2>/dev/null || echo "MyPy not yet installed"

echo "Development environment ready!"
echo "Use 'pipenv shell' to activate the virtual environment"