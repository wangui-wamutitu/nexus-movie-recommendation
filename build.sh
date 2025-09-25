#!/usr/bin/env bash
# build.sh - Render build script for Movie Recommendation API

set -o errexit  # exit on error

echo "Starting build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Populate initial data (optional - only on first deploy)
echo "Populating movie data..."
python manage.py populate_movies --pages 2 --categories popular trending

echo "Build completed successfully!"