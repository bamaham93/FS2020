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
        lines = f.readlines()
    
    # Find the start of actual Bible text (skip table of contents)
    # Look for the first occurrence of "The First Book of Moses: Called Genesis" 
    # followed by a verse (1:1)
    start_idx = 0
    for i, line in enumerate(lines):
        if 'The First Book of Moses: Called Genesis' in line:
            # Check if there's a verse nearby
            for j in range(i, min(i+10, len(lines))):
                if re.match(r'^\s*1:1\s+', lines[j]):
                    start_idx = i
                    break
            if start_idx > 0:
                break
    
    print(f"Starting parsing at line {start_idx}")
    lines = lines[start_idx:]
    
    # Build book header patterns for precise matching
    # This prevents false positives from verse text
    book_patterns = {
        'Genesis': r'^The First Book of Moses:\s*Called Genesis\s*$',
        'Exodus': r'^The Second Book of Moses:\s*Called Exodus\s*$',
        'Leviticus': r'^The Third Book of Moses:\s*Called Leviticus\s*$',
        'Numbers': r'^The Fourth Book of Moses:\s*Called Numbers\s*$',
        'Deuteronomy': r'^The Fifth Book of Moses:\s*Called Deuteronomy\s*$',
        'Joshua': r'^The Book of Joshua\s*$',
        'Judges': r'^The Book of Judges\s*$',
        'Ruth': r'^The Book of Ruth\s*$',
        '1 Samuel': r'^The First Book of Samuel\s*$',
        '2 Samuel': r'^The Second Book of Samuel\s*$',
        '1 Kings': r'^The First Book of the Kings\s*$',
        '2 Kings': r'^The Second Book of the Kings\s*$',
        '1 Chronicles': r'^The First Book of the Chronicles\s*$',
        '2 Chronicles': r'^The Second Book of the Chronicles\s*$',
        'Ezra': r'^Ezra\s*$',
        'Nehemiah': r'^The Book of Nehemiah\s*$',
        'Esther': r'^The Book of Esther\s*$',
        'Job': r'^The Book of Job\s*$',
        'Psalms': r'^The Book of Psalms\s*$',
        'Proverbs': r'^The Proverbs\s*$',
        'Ecclesiastes': r'^Ecclesiastes\s*$',
        'Song of Solomon': r'^The Song of Solomon\s*$',
        'Isaiah': r'^The Book of the Prophet Isaiah\s*$',
        'Jeremiah': r'^The Book of the Prophet Jeremiah\s*$',
        'Lamentations': r'^The Lamentations of Jeremiah\s*$',
        'Ezekiel': r'^The Book of the Prophet Ezekiel\s*$',
        'Daniel': r'^The Book of Daniel\s*$',
        'Hosea': r'^Hosea\s*$',
        'Joel': r'^Joel\s*$',
        'Amos': r'^Amos\s*$',
        'Obadiah': r'^Obadiah\s*$',
        'Jonah': r'^Jonah\s*$',
        'Micah': r'^Micah\s*$',
        'Nahum': r'^Nahum\s*$',
        'Habakkuk': r'^Habakkuk\s*$',
        'Zephaniah': r'^Zephaniah\s*$',
        'Haggai': r'^Haggai\s*$',
        'Zechariah': r'^Zechariah\s*$',
        'Malachi': r'^Malachi\s*$',
        'Matthew': r'^The Gospel According to Saint Matthew\s*$',
        'Mark': r'^The Gospel According to Saint Mark\s*$',
        'Luke': r'^The Gospel According to Saint Luke\s*$',
        'John': r'^The Gospel According to Saint John\s*$',
        'Acts': r'^The Acts of the Apostles\s*$',
        'Romans': r'^The Epistle of Paul the Apostle to the Romans\s*$',
        '1 Corinthians': r'^The First Epistle of Paul the Apostle to the Corinthians\s*$',
        '2 Corinthians': r'^The Second Epistle of Paul the Apostle to the Corinthians\s*$',
        'Galatians': r'^The Epistle of Paul the Apostle to the Galatians\s*$',
        'Ephesians': r'^The Epistle of Paul the Apostle to the Ephesians\s*$',
        'Philippians': r'^The Epistle of Paul the Apostle to the Philippians\s*$',
        'Colossians': r'^The Epistle of Paul the Apostle to the Colossians\s*$',
        '1 Thessalonians': r'^The First Epistle of Paul the Apostle to the Thessalonians\s*$',
        '2 Thessalonians': r'^The Second Epistle of Paul the Apostle to the Thessalonians\s*$',
        '1 Timothy': r'^The First Epistle of Paul the Apostle to Timothy\s*$',
        '2 Timothy': r'^The Second Epistle of Paul the Apostle to Timothy\s*$',
        'Titus': r'^The Epistle of Paul the Apostle to Titus\s*$',
        'Philemon': r'^The Epistle of Paul the Apostle to Philemon\s*$',
        'Hebrews': r'^The Epistle of Paul the Apostle to the Hebrews\s*$',
        'James': r'^The General Epistle of James\s*$',
        '1 Peter': r'^The First Epistle General of Peter\s*$',
        '2 Peter': r'^The Second General Epistle of Peter\s*$',
        '1 John': r'^The First Epistle General of John\s*$',
        '2 John': r'^The Second Epistle General of John\s*$',
        '3 John': r'^The Third Epistle General of John\s*$',
        'Jude': r'^The General Epistle of Jude\s*$',
        'Revelation': r'^The Revelation of Saint John the Divine\s*$',
    }
    
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
    
    # Track if we're in a "Commonly Called" or "Otherwise Called" section
    skip_next_header = False
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Check for "Commonly Called" or "Otherwise Called" markers
        if re.match(r'^(Commonly Called:|Otherwise Called:)\s*$', line_stripped):
            skip_next_header = True
            print(f"DEBUG: Setting skip_next_header=True at: {line_stripped}")
            continue
        
        # Check for book headers using precise patterns
        book_matched = False
        for book_name, pattern in book_patterns.items():
            if re.match(pattern, line_stripped):
                # Skip if this is an alternate title
                if skip_next_header:
                    print(f"Skipping alternate title: {line_stripped}")
                    skip_next_header = False
                    book_matched = True
                    break
                
                # Save any pending verse before switching books
                save_current_verse()
                current_verse = None
                current_verse_text = []
                
                current_book = book_name
                current_chapter = 0
                print(f"Found book: {book_name}")
                book_matched = True
                break
        
        if book_matched:
            continue
        
        # Check for chapter:verse pattern: "1:1", "2:3", etc.
        verse_match = re.match(r'^(\d+):(\d+)\s+(.+)$', line_stripped)
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
        elif current_verse and current_book and line_stripped:
            # This is a continuation of the current verse
            current_verse_text.append(line_stripped)
    
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
