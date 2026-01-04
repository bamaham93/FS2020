"""
Parser for Project Gutenberg KJV Bible text format.

The Project Gutenberg KJV file (pg10.txt) has this structure:
- Header with copyright/license info
- "The First Book of Moses: Called Genesis" (book titles)
- Chapter markers: "1:1", "1:2", etc.
- Verse text follows the reference
"""

import re


# Bible book metadata: (name, slug, order, testament, chapters)
BIBLE_BOOKS = [
    # Old Testament
    ("Genesis", "genesis", 1, "OT", 50),
    ("Exodus", "exodus", 2, "OT", 40),
    ("Leviticus", "leviticus", 3, "OT", 27),
    ("Numbers", "numbers", 4, "OT", 36),
    ("Deuteronomy", "deuteronomy", 5, "OT", 34),
    ("Joshua", "joshua", 6, "OT", 24),
    ("Judges", "judges", 7, "OT", 21),
    ("Ruth", "ruth", 8, "OT", 4),
    ("1 Samuel", "1-samuel", 9, "OT", 31),
    ("2 Samuel", "2-samuel", 10, "OT", 24),
    ("1 Kings", "1-kings", 11, "OT", 22),
    ("2 Kings", "2-kings", 12, "OT", 25),
    ("1 Chronicles", "1-chronicles", 13, "OT", 29),
    ("2 Chronicles", "2-chronicles", 14, "OT", 36),
    ("Ezra", "ezra", 15, "OT", 10),
    ("Nehemiah", "nehemiah", 16, "OT", 13),
    ("Esther", "esther", 17, "OT", 10),
    ("Job", "job", 18, "OT", 42),
    ("Psalms", "psalms", 19, "OT", 150),
    ("Proverbs", "proverbs", 20, "OT", 31),
    ("Ecclesiastes", "ecclesiastes", 21, "OT", 12),
    ("Song of Solomon", "song-of-solomon", 22, "OT", 8),
    ("Isaiah", "isaiah", 23, "OT", 66),
    ("Jeremiah", "jeremiah", 24, "OT", 52),
    ("Lamentations", "lamentations", 25, "OT", 5),
    ("Ezekiel", "ezekiel", 26, "OT", 48),
    ("Daniel", "daniel", 27, "OT", 12),
    ("Hosea", "hosea", 28, "OT", 14),
    ("Joel", "joel", 29, "OT", 3),
    ("Amos", "amos", 30, "OT", 9),
    ("Obadiah", "obadiah", 31, "OT", 1),
    ("Jonah", "jonah", 32, "OT", 4),
    ("Micah", "micah", 33, "OT", 7),
    ("Nahum", "nahum", 34, "OT", 3),
    ("Habakkuk", "habakkuk", 35, "OT", 3),
    ("Zephaniah", "zephaniah", 36, "OT", 3),
    ("Haggai", "haggai", 37, "OT", 2),
    ("Zechariah", "zechariah", 38, "OT", 14),
    ("Malachi", "malachi", 39, "OT", 4),
    # New Testament
    ("Matthew", "matthew", 40, "NT", 28),
    ("Mark", "mark", 41, "NT", 16),
    ("Luke", "luke", 42, "NT", 24),
    ("John", "john", 43, "NT", 21),
    ("Acts", "acts", 44, "NT", 28),
    ("Romans", "romans", 45, "NT", 16),
    ("1 Corinthians", "1-corinthians", 46, "NT", 16),
    ("2 Corinthians", "2-corinthians", 47, "NT", 13),
    ("Galatians", "galatians", 48, "NT", 6),
    ("Ephesians", "ephesians", 49, "NT", 6),
    ("Philippians", "philippians", 50, "NT", 4),
    ("Colossians", "colossians", 51, "NT", 4),
    ("1 Thessalonians", "1-thessalonians", 52, "NT", 5),
    ("2 Thessalonians", "2-thessalonians", 53, "NT", 3),
    ("1 Timothy", "1-timothy", 54, "NT", 6),
    ("2 Timothy", "2-timothy", 55, "NT", 4),
    ("Titus", "titus", 56, "NT", 3),
    ("Philemon", "philemon", 57, "NT", 1),
    ("Hebrews", "hebrews", 58, "NT", 13),
    ("James", "james", 59, "NT", 5),
    ("1 Peter", "1-peter", 60, "NT", 5),
    ("2 Peter", "2-peter", 61, "NT", 3),
    ("1 John", "1-john", 62, "NT", 5),
    ("2 John", "2-john", 63, "NT", 1),
    ("3 John", "3-john", 64, "NT", 1),
    ("Jude", "jude", 65, "NT", 1),
    ("Revelation", "revelation", 66, "NT", 22),
]

# Create lookup dictionary
BOOK_INFO = {name: (slug, order, testament, chapters) for name, slug, order, testament, chapters in BIBLE_BOOKS}


def parse_gutenberg_kjv(file_path):
    """
    Parse Project Gutenberg KJV Bible text file.
    
    Returns list of book dictionaries compatible with import_kjv command.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find where the actual Bible text starts (after header)
    # Usually starts with "The First Book of Moses"
    start_marker = content.find("The First Book of Moses")
    if start_marker == -1:
        start_marker = content.find("Genesis")
    if start_marker == -1:
        start_marker = 0
    
    content = content[start_marker:]
    
    # Parse the content
    books_data = {}
    current_book = None
    current_chapter = 0
    current_verse = None
    current_verse_text = []
    
    def save_current_verse():
        """Helper to save the accumulated verse text."""
        if current_book and current_verse:
            if current_book not in books_data:
                slug, order, testament, chapters = BOOK_INFO[current_book]
                books_data[current_book] = {
                    'name': current_book,
                    'slug': slug,
                    'order': order,
                    'testament': testament,
                    'chapters': chapters,
                    'verses': []
                }
            
            books_data[current_book]['verses'].append({
                'chapter': current_verse['chapter'],
                'verse': current_verse['verse'],
                'text': ' '.join(current_verse_text).strip()
            })
    
    # Split into lines
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check for book title patterns
        # e.g., "The First Book of Moses: Called Genesis"
        # or "The Gospel According to Saint John"
        for book_name in BOOK_INFO.keys():
            if book_name.lower() in line.lower():
                # Check if this looks like a book header
                if any(keyword in line.lower() for keyword in ['book of', 'gospel', 'epistle', 'revelation']):
                    # Save any pending verse before switching books
                    save_current_verse()
                    current_verse = None
                    current_verse_text = []
                    
                    current_book = book_name
                    current_chapter = 0
                    print(f"Found book: {book_name}")
                    break
        
        # Check for chapter:verse pattern: "1:1", "2:3", etc.
        verse_match = re.match(r'^(\d+):(\d+)\s+(.+)$', line)
        if verse_match and current_book:
            # Save previous verse before starting new one
            save_current_verse()
            
            chapter = int(verse_match.group(1))
            verse_num = int(verse_match.group(2))
            text = verse_match.group(3).strip()
            
            # Update current chapter
            if chapter != current_chapter:
                current_chapter = chapter
            
            # Start new verse
            current_verse = {
                'chapter': chapter,
                'verse': verse_num
            }
            current_verse_text = [text]
        elif current_verse and current_book and line:
            # This is a continuation of the current verse
            # Check if it's not the start of a new book
            is_book_header = any(
                book_name.lower() in line.lower() and 
                any(keyword in line.lower() for keyword in ['book of', 'gospel', 'epistle'])
                for book_name in BOOK_INFO.keys()
            )
            if not is_book_header:
                current_verse_text.append(line)
    
    # Save the last verse
    save_current_verse()
    
    return list(books_data.values())


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        result = parse_gutenberg_kjv(sys.argv[1])
        print(f"Parsed {len(result)} books")
        for book in result[:3]:
            print(f"{book['name']}: {len(book['verses'])} verses")
