#!/bin/bash

# Build file for Vercel deployment
echo "Starting Django build process..."

# Install dependencies
pip install -r requirements.txt

# Create static files directory
mkdir -p staticfiles_build

# Collect static files
python manage.py collectstatic --noinput --clear

echo "Build process completed!"
