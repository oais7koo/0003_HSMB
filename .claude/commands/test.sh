#!/bin/bash
# Run project tests

echo "Running Python tests..."

# Check if in pipenv environment
if [ -z "$PIPENV_ACTIVE" ]; then
    echo "Activating pipenv environment..."
    pipenv run pytest "$@"
else
    pytest "$@"
fi