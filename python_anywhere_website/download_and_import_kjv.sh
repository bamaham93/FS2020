#!/bin/bash
# Script to download and import the complete KJV Bible from Project Gutenberg
# Usage: ./download_and_import_kjv.sh

set -e  # Exit on error

echo "=========================================="
echo "KJV Bible Import Script"
echo "=========================================="
echo ""

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the python_anywhere_website directory."
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

# Download the KJV text from Project Gutenberg
echo "Step 1: Downloading KJV Bible text from Project Gutenberg..."
echo "URL: https://www.gutenberg.org/cache/epub/10/pg10.txt"
echo ""

if [ -f "data/pg10.txt" ]; then
    echo "File data/pg10.txt already exists."
    read -p "Do you want to re-download it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        curl -L "https://www.gutenberg.org/cache/epub/10/pg10.txt" -o data/pg10.txt
        echo "✓ Download complete"
    else
        echo "✓ Using existing file"
    fi
else
    curl -L "https://www.gutenberg.org/cache/epub/10/pg10.txt" -o data/pg10.txt
    echo "✓ Download complete"
fi

echo ""

# Check file size
FILE_SIZE=$(stat -f%z "data/pg10.txt" 2>/dev/null || stat -c%s "data/pg10.txt" 2>/dev/null)
echo "Downloaded file size: $FILE_SIZE bytes"
echo ""

# Import the data
echo "Step 2: Importing KJV Bible into database..."
echo "This will take 2-5 minutes for ~31,000 verses..."
echo ""

read -p "Clear existing Bible data before importing? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Importing with --clear flag..."
    python manage.py import_kjv --file data/pg10.txt --format gutenberg --clear
else
    echo "Importing without clearing (will skip duplicates)..."
    python manage.py import_kjv --file data/pg10.txt --format gutenberg
fi

echo ""
echo "=========================================="
echo "✓ Import complete!"
echo "=========================================="
echo ""
echo "You can now:"
echo "  - Visit /bible/ to browse the Bible"
echo "  - Access the API at /api/v1/bible/books"
echo ""
