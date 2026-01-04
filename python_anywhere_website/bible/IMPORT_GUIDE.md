# KJV Bible Import Guide

This guide explains how to import KJV Bible text into the application.

## Quick Start (Easiest Way)

We've provided helper scripts to download and import the complete KJV Bible in one command:

### Option 1: Bash Script
```bash
cd python_anywhere_website
./download_and_import_kjv.sh
```

### Option 2: Python Script
```bash
cd python_anywhere_website
python download_and_import_kjv.py
```

Both scripts will:
1. Download the KJV text from Project Gutenberg
2. Prompt you to clear existing data (optional)
3. Import all 66 books and ~31,000 verses (takes 2-5 minutes)

That's it! The Bible is now ready to browse at `/bible/`

---

## Manual Import (Advanced Users)

If you prefer to do it manually or customize the process:

## Import Command

```bash
python manage.py import_kjv [options]
```

### Options

- `--file <path>` : Path to the data file
- `--format <format>` : Format of the file (json, csv, txt, or auto)
- `--clear` : Clear existing Bible data before importing

### Examples

```bash
# Import from JSON file
python manage.py import_kjv --file data/kjv.json --format json --clear

# Import from CSV (auto-detect format)
python manage.py import_kjv --file data/kjv.csv --clear

# Import from text file
python manage.py import_kjv --file data/kjv.txt --format txt --clear

# Use sample data (no file)
python manage.py import_kjv --clear
```

## Supported File Formats

### 1. Project Gutenberg KJV (Recommended)

**This is the easiest way to get the complete KJV Bible!**

Download the official Project Gutenberg KJV text:

```bash
# Download the file
curl -O https://www.gutenberg.org/cache/epub/10/pg10.txt

# Import it (auto-detects Gutenberg format)
python manage.py import_kjv --file pg10.txt --clear

# Or explicitly specify the format
python manage.py import_kjv --file pg10.txt --format gutenberg --clear
```

The parser automatically:
- Removes the Project Gutenberg header
- Identifies all 66 books
- Parses the `Chapter:Verse Text` format
- Imports all ~31,000 verses

**Expected import time**: 2-5 minutes for the full Bible.

### 2. JSON Format

The most flexible format for custom data. Each book is an object with verses array.

```json
[
  {
    "name": "Genesis",
    "slug": "genesis",
    "order": 1,
    "testament": "OT",
    "chapters": 50,
    "verses": [
      {
        "chapter": 1,
        "verse": 1,
        "text": "In the beginning God created the heaven and the earth."
      },
      {
        "chapter": 1,
        "verse": 2,
        "text": "And the earth was without form, and void..."
      }
    ]
  },
  {
    "name": "John",
    "slug": "john",
    "order": 43,
    "testament": "NT",
    "chapters": 21,
    "verses": [
      {
        "chapter": 1,
        "verse": 1,
        "text": "In the beginning was the Word..."
      }
    ]
  }
]
```

### 3. CSV Format

Simple tabular format. Headers required.

```csv
book_name,book_slug,book_order,testament,chapter,verse,text
Genesis,genesis,1,OT,1,1,"In the beginning God created the heaven and the earth."
Genesis,genesis,1,OT,1,2,"And the earth was without form, and void; and darkness was upon the face of the deep."
John,john,43,NT,1,1,"In the beginning was the Word, and the Word was with God, and the Word was God."
John,john,43,NT,3,16,"For God so loved the world, that he gave his only begotten Son..."
```

### 4. Plain Text Format

Simple one-line-per-verse format:

```text
Genesis 1:1 In the beginning God created the heaven and the earth.
Genesis 1:2 And the earth was without form, and void; and darkness was upon the face of the deep.
Genesis 1:3 And God said, Let there be light: and there was light.
Exodus 1:1 Now these are the names of the children of Israel...
John 1:1 In the beginning was the Word, and the Word was with God, and the Word was God.
John 3:16 For God so loved the world, that he gave his only begotten Son...
```

Format: `BookName Chapter:Verse TextContent`

## Where to Get KJV Text

### Option 1: Project Gutenberg
The best source for public domain KJV text.

1. Visit: https://www.gutenberg.org/ebooks/10
2. Download as "Plain Text UTF-8"
3. You'll need to parse and format it into one of the supported formats above

### Option 2: Pre-formatted Datasets

Search for "KJV Bible JSON" or "KJV Bible CSV" online. Many free datasets exist:

- **GitHub**: Search for "kjv-bible-json" repositories
- **Kaggle**: Bible datasets in CSV format
- **Open Bible APIs**: Some provide downloadable datasets

### Option 3: Convert from HTML/Web Source

If you have a link to the full text on one page:

1. Copy the text from the webpage
2. Format it according to one of the formats above
3. The simplest is the plain text format: `Book Chapter:Verse Text`

## Example: Converting a Web Page to Text Format

If you have HTML like:
```html
<div class="verse" data-book="Genesis" data-chapter="1" data-verse="1">
  In the beginning God created the heaven and the earth.
</div>
```

Convert to:
```text
Genesis 1:1 In the beginning God created the heaven and the earth.
```

## Tips

1. **Start small**: Test with a single book first
2. **Validate**: Check that chapter and verse numbers are correct
3. **Clean text**: Remove footnotes, headers, and non-Scripture content
4. **Encoding**: Use UTF-8 encoding for all files
5. **Incremental import**: The command won't duplicate existing verses

## Book Order Reference

Old Testament (1-39):
- Genesis (1), Exodus (2), Leviticus (3), Numbers (4), Deuteronomy (5)
- Joshua (6), Judges (7), Ruth (8), 1 Samuel (9), 2 Samuel (10)
- ... (continue through Malachi at 39)

New Testament (40-66):
- Matthew (40), Mark (41), Luke (42), John (43), Acts (44)
- Romans (45), 1 Corinthians (46), 2 Corinthians (47)
- ... (continue through Revelation at 66)

## Troubleshooting

### Error: "File not found"
- Check the file path is correct
- Use absolute paths if relative paths don't work

### Error: "Invalid JSON"
- Validate your JSON at https://jsonlint.com
- Ensure proper quotes and commas

### Import is slow
- This is normal for 31,000+ verses
- The bulk_create operation should take 1-2 minutes for full Bible

### Verses appear in wrong order
- Ensure your data is sorted by book order, chapter, then verse
- The display will order by book.order, chapter, verse

## Need Help?

Please share:
1. The format of your source data (link or sample)
2. Any error messages you receive
3. Whether you need help converting the data

I can help write a custom parser if your data format is different.
