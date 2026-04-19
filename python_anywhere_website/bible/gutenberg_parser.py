import re

VERSE_TOKEN = re.compile(r"(\d+):(\d+)\s")  # chapter:verse + at least one space


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
        raise RuntimeError("Could not find Bible text start (Genesis header + 1:1).")

    lines = lines[start_idx:]

    # ---- 2) Your existing book_patterns dict (keep as-is) ----
    # IMPORTANT: use the same dict you already have in your file
    book_patterns = {
        # ... paste your entire book_patterns dict here unchanged ...
    }

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
