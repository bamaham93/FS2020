#!/usr/bin/env python
"""
Download and import the complete KJV Bible from Project Gutenberg.
Usage: python download_and_import_kjv.py [--no-clear]
"""

import sys
import os
import urllib.request
import subprocess
from pathlib import Path


def download_kjv():
    """Download the KJV text from Project Gutenberg."""
    url = "https://www.gutenberg.org/cache/epub/10/pg10.txt"
    output_file = Path("data/pg10.txt")

    # Create data directory
    output_file.parent.mkdir(exist_ok=True)

    # Check if file already exists
    if output_file.exists():
        print(f"File {output_file} already exists.")
        response = input("Do you want to re-download it? (y/n): ").lower()
        if response != "y":
            print("✓ Using existing file")
            return str(output_file)

    print(f"Downloading KJV Bible from Project Gutenberg...")
    print(f"URL: {url}")

    try:
        urllib.request.urlretrieve(url, output_file)
        file_size = output_file.stat().st_size
        print(f"✓ Download complete ({file_size:,} bytes)")
        return str(output_file)
    except Exception as e:
        print(f"✗ Error downloading file: {e}")
        print("\nAlternative: Download manually with:")
        print(f"  curl -O {url}")
        print(f"  mv pg10.txt {output_file}")
        sys.exit(1)


def import_kjv(file_path, clear=True):
    """Import the KJV text into the database."""
    print("\nImporting KJV Bible into database...")
    print("This will take 2-5 minutes for ~31,000 verses...")

    cmd = [
        sys.executable,
        "manage.py",
        "import_kjv",
        "--file",
        file_path,
        "--format",
        "gutenberg",
    ]

    if clear:
        response = input(
            "\nClear existing Bible data before importing? (y/n): "
        ).lower()
        if response == "y":
            cmd.append("--clear")
            print("Importing with --clear flag...")
        else:
            print("Importing without clearing (will skip duplicates)...")

    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✓ Import complete!")
        print("=" * 50)
        print("\nYou can now:")
        print("  - Visit /bible/ to browse the Bible")
        print("  - Access the API at /api/v1/bible/books")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error during import: {e}")
        sys.exit(1)


def main():
    print("=" * 50)
    print("KJV Bible Import Script")
    print("=" * 50)
    print()

    # Check if manage.py exists
    if not Path("manage.py").exists():
        print("Error: manage.py not found.")
        print("Please run this script from the python_anywhere_website directory.")
        sys.exit(1)

    # Check command line args
    clear = "--no-clear" not in sys.argv

    # Download the file
    file_path = download_kjv()

    # Import the data
    import_kjv(file_path, clear)


if __name__ == "__main__":
    main()
