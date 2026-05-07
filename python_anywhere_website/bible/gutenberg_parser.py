import re

VERSE_TOKEN = re.compile(r"(\d+):(\d+)\s")  # chapter:verse + at least one space

# Maps canonical book name -> (slug, order, testament, chapters)
BOOK_INFO = {
    # Old Testament
    "Genesis": ("genesis", 1, "OT", 50),
    "Exodus": ("exodus", 2, "OT", 40),
    "Leviticus": ("leviticus", 3, "OT", 27),
    "Numbers": ("numbers", 4, "OT", 36),
    "Deuteronomy": ("deuteronomy", 5, "OT", 34),
    "Joshua": ("joshua", 6, "OT", 24),
    "Judges": ("judges", 7, "OT", 21),
    "Ruth": ("ruth", 8, "OT", 4),
    "1 Samuel": ("1-samuel", 9, "OT", 31),
    "2 Samuel": ("2-samuel", 10, "OT", 24),
    "1 Kings": ("1-kings", 11, "OT", 22),
    "2 Kings": ("2-kings", 12, "OT", 25),
    "1 Chronicles": ("1-chronicles", 13, "OT", 29),
    "2 Chronicles": ("2-chronicles", 14, "OT", 36),
    "Ezra": ("ezra", 15, "OT", 10),
    "Nehemiah": ("nehemiah", 16, "OT", 13),
    "Esther": ("esther", 17, "OT", 10),
    "Job": ("job", 18, "OT", 42),
    "Psalms": ("psalms", 19, "OT", 150),
    "Proverbs": ("proverbs", 20, "OT", 31),
    "Ecclesiastes": ("ecclesiastes", 21, "OT", 12),
    "Song of Solomon": ("song-of-solomon", 22, "OT", 8),
    "Isaiah": ("isaiah", 23, "OT", 66),
    "Jeremiah": ("jeremiah", 24, "OT", 52),
    "Lamentations": ("lamentations", 25, "OT", 5),
    "Ezekiel": ("ezekiel", 26, "OT", 48),
    "Daniel": ("daniel", 27, "OT", 12),
    "Hosea": ("hosea", 28, "OT", 14),
    "Joel": ("joel", 29, "OT", 3),
    "Amos": ("amos", 30, "OT", 9),
    "Obadiah": ("obadiah", 31, "OT", 1),
    "Jonah": ("jonah", 32, "OT", 4),
    "Micah": ("micah", 33, "OT", 7),
    "Nahum": ("nahum", 34, "OT", 3),
    "Habakkuk": ("habakkuk", 35, "OT", 3),
    "Zephaniah": ("zephaniah", 36, "OT", 3),
    "Haggai": ("haggai", 37, "OT", 2),
    "Zechariah": ("zechariah", 38, "OT", 14),
    "Malachi": ("malachi", 39, "OT", 4),
    # New Testament
    "Matthew": ("matthew", 40, "NT", 28),
    "Mark": ("mark", 41, "NT", 16),
    "Luke": ("luke", 42, "NT", 24),
    "John": ("john", 43, "NT", 21),
    "Acts": ("acts", 44, "NT", 28),
    "Romans": ("romans", 45, "NT", 16),
    "1 Corinthians": ("1-corinthians", 46, "NT", 16),
    "2 Corinthians": ("2-corinthians", 47, "NT", 13),
    "Galatians": ("galatians", 48, "NT", 6),
    "Ephesians": ("ephesians", 49, "NT", 6),
    "Philippians": ("philippians", 50, "NT", 4),
    "Colossians": ("colossians", 51, "NT", 4),
    "1 Thessalonians": ("1-thessalonians", 52, "NT", 5),
    "2 Thessalonians": ("2-thessalonians", 53, "NT", 3),
    "1 Timothy": ("1-timothy", 54, "NT", 6),
    "2 Timothy": ("2-timothy", 55, "NT", 4),
    "Titus": ("titus", 56, "NT", 3),
    "Philemon": ("philemon", 57, "NT", 1),
    "Hebrews": ("hebrews", 58, "NT", 13),
    "James": ("james", 59, "NT", 5),
    "1 Peter": ("1-peter", 60, "NT", 5),
    "2 Peter": ("2-peter", 61, "NT", 3),
    "1 John": ("1-john", 62, "NT", 5),
    "2 John": ("2-john", 63, "NT", 1),
    "3 John": ("3-john", 64, "NT", 1),
    "Jude": ("jude", 65, "NT", 1),
    "Revelation": ("revelation", 66, "NT", 22),
}

# Maps canonical book name -> regex pattern matching the Project Gutenberg header line.
# Patterns are anchored (^...$) to prevent partial matches.
book_patterns = {
    # Old Testament
    "Genesis": r"^The First Book of Moses: Called Genesis$",
    "Exodus": r"^The Second Book of Moses: Called Exodus$",
    "Leviticus": r"^The Third Book of Moses: Called Leviticus$",
    "Numbers": r"^The Fourth Book of Moses: Called Numbers$",
    "Deuteronomy": r"^The Fifth Book of Moses: Called Deuteronomy$",
    "Joshua": r"^The Book of Joshua$",
    "Judges": r"^The Book of Judges$",
    "Ruth": r"^The Book of Ruth$",
    "1 Samuel": r"^The First Book of Samuel$",
    "2 Samuel": r"^The Second Book of Samuel$",
    "1 Kings": r"^The First Book of the Kings$",
    "2 Kings": r"^The Second Book of the Kings$",
    "1 Chronicles": r"^The First Book of the Chronicles$",
    "2 Chronicles": r"^The Second Book of the Chronicles$",
    "Ezra": r"^Ezra$",
    "Nehemiah": r"^The Book of Nehemiah$",
    "Esther": r"^The Book of Esther$",
    "Job": r"^The Book of Job$",
    "Psalms": r"^The Book of Psalms$",
    "Proverbs": r"^The Proverbs$",
    "Ecclesiastes": r"^Ecclesiastes$",
    "Song of Solomon": r"^The Song of Solomon$",
    "Isaiah": r"^The Book of the Prophet Isaiah$",
    "Jeremiah": r"^The Book of the Prophet Jeremiah$",
    "Lamentations": r"^The Lamentations of Jeremiah$",
    "Ezekiel": r"^The Book of the Prophet Ezekiel$",
    "Daniel": r"^The Book of Daniel$",
    "Hosea": r"^Hosea$",
    "Joel": r"^Joel$",
    "Amos": r"^Amos$",
    "Obadiah": r"^Obadiah$",
    "Jonah": r"^Jonah$",
    "Micah": r"^Micah$",
    "Nahum": r"^Nahum$",
    "Habakkuk": r"^Habakkuk$",
    "Zephaniah": r"^Zephaniah$",
    "Haggai": r"^Haggai$",
    "Zechariah": r"^Zechariah$",
    "Malachi": r"^Malachi$",
    # New Testament
    "Matthew": r"^The Gospel According to Saint Matthew$",
    "Mark": r"^The Gospel According to Saint Mark$",
    "Luke": r"^The Gospel According to Saint Luke$",
    "John": r"^The Gospel According to Saint John$",
    "Acts": r"^The Acts of the Apostles$",
    "Romans": r"^The Epistle of Paul the Apostle to the Romans$",
    "1 Corinthians": r"^The First Epistle of Paul the Apostle to the Corinthians$",
    "2 Corinthians": r"^The Second Epistle of Paul the Apostle to the Corinthians$",
    "Galatians": r"^The Epistle of Paul the Apostle to the Galatians$",
    "Ephesians": r"^The Epistle of Paul the Apostle to the Ephesians$",
    "Philippians": r"^The Epistle of Paul the Apostle to the Philippians$",
    "Colossians": r"^The Epistle of Paul the Apostle to the Colossians$",
    "1 Thessalonians": r"^The First Epistle of Paul the Apostle to the Thessalonians$",
    "2 Thessalonians": r"^The Second Epistle of Paul the Apostle to the Thessalonians$",
    "1 Timothy": r"^The First Epistle of Paul the Apostle to Timothy$",
    "2 Timothy": r"^The Second Epistle of Paul the Apostle to Timothy$",
    "Titus": r"^The Epistle of Paul the Apostle to Titus$",
    "Philemon": r"^The Epistle of Paul the Apostle to Philemon$",
    "Hebrews": r"^The Epistle of Paul the Apostle to the Hebrews$",
    "James": r"^The General Epistle of James$",
    "1 Peter": r"^The First Epistle General of Peter$",
    "2 Peter": r"^The Second General Epistle of Peter$",
    "1 John": r"^The First Epistle General of John$",
    "2 John": r"^The Second Epistle General of John$",
    "3 John": r"^The Third Epistle General of John$",
    "Jude": r"^The General Epistle of Jude$",
    "Revelation": r"^The Revelation of Saint John the Divine$",
}


def parse_gutenberg_kjv(file_path, debug=False):
    """
    Parse Project Gutenberg KJV (pg10.txt).

    Key fixes:
    - Find the *real* start of Bible text (Genesis header + nearby 1:1) to skip TOC.
    - Split lines that contain MULTIPLE verse markers (common in Romans, epistles, etc).
    """

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # ---- 1) Find real start of Bible text (skip TOC) ----
    start_idx = None
    for i, line in enumerate(lines):
        if "The First Book of Moses: Called Genesis" in line:
            # Look ahead for a real verse line
            for j in range(i, min(i + 30, len(lines))):
                if re.match(r"^\s*1:1\s+", lines[j]):
                    start_idx = i
                    break
        if start_idx is not None:
            break

    if start_idx is None:
        # No Genesis header found; treat the whole file as Bible content.
        start_idx = 0

    lines = lines[start_idx:]

    # ---- State ----
    books_data = {}
    current_book = None
    current_verse = None  # dict {chapter:int, verse:int}
    current_verse_text_parts = []
    in_alternate_section = False

    # diagnostics
    dbg_book_hits = 0
    dbg_verses_saved = 0

    def ensure_book(book_name):
        if book_name not in books_data:
            slug, order, testament, chapters = BOOK_INFO[book_name]
            books_data[book_name] = {
                "name": book_name,
                "slug": slug,
                "order": order,
                "testament": testament,
                "chapters": chapters,
                "verses": [],
            }

    def save_current_verse():
        nonlocal dbg_verses_saved, current_verse, current_verse_text_parts
        if current_book and current_verse:
            text = " ".join(current_verse_text_parts).strip()
            ensure_book(current_book)
            books_data[current_book]["verses"].append(
                {
                    "chapter": current_verse["chapter"],
                    "verse": current_verse["verse"],
                    "text": text,
                }
            )
            dbg_verses_saved += 1

    def start_new_verse(chapter, verse, initial_text):
        nonlocal current_verse, current_verse_text_parts
        save_current_verse()
        current_verse = {"chapter": chapter, "verse": verse}
        current_verse_text_parts = []
        if initial_text:
            current_verse_text_parts.append(initial_text)

    # ---- Main parse loop ----
    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # Alternate-title markers (your existing behavior)
        if re.match(r"^(Commonly Called:|Otherwise Called:)\s*$", line):
            in_alternate_section = True
            continue

        # Book header detection (exact patterns)
        matched_book = None
        for book_name, pattern in book_patterns.items():
            if re.match(pattern, line):
                matched_book = book_name
                break

        if matched_book:
            # If this header is an alternate title, ignore it
            if in_alternate_section:
                in_alternate_section = False
                continue

            # Real book change
            save_current_verse()
            current_book = matched_book
            current_verse = None
            current_verse_text_parts = []
            in_alternate_section = False

            dbg_book_hits += 1
            if debug:
                print(f"[BOOK] {current_book}")
            continue

        # If we don't know which book we're in yet, we can't store verses
        if not current_book:
            continue

        # Split by EVERY verse token found in the line (Romans/epistles do this constantly)
        matches = list(VERSE_TOKEN.finditer(line))
        if matches:
            for idx, m in enumerate(matches):
                chap = int(m.group(1))
                vs = int(m.group(2))
                start = m.end()
                end = matches[idx + 1].start() if idx + 1 < len(matches) else len(line)
                chunk = line[start:end].strip()

                start_new_verse(chap, vs, chunk)

            in_alternate_section = False
        else:
            # Continuation line for current verse
            if current_verse:
                current_verse_text_parts.append(line)

    save_current_verse()

    if debug:
        total_books = len(books_data)
        total_verses = sum(len(b["verses"]) for b in books_data.values())
        print(
            f"[DONE] books={total_books}, verses={total_verses}, book_hits={dbg_book_hits}"
        )

    return list(books_data.values())
