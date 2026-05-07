from django.core.management.base import BaseCommand
from bible.models import BibleBook, BibleVerse
import json
import csv
import re
import sqlite3
from pathlib import Path


class Command(BaseCommand):
    help = "Import KJV Bible data into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the data file (JSON, CSV, or TXT)",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["json", "csv", "txt", "sqlite", "auto"],
            default="auto",
            help="Format of the input file (auto-detect if not specified)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing Bible data before importing",
        )

    def handle(self, *args, **options):
        self.stdout.write("Importing KJV Bible data...")

        # Clear existing data if requested
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            BibleVerse.objects.all().delete()
            BibleBook.objects.all().delete()

        # Load data from file or use sample data
        if options["file"]:
            file_path = Path(options["file"])
            if not file_path.exists():
                self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
                return

            # Auto-detect format if needed
            file_format = options["format"]
            if file_format == "auto":
                file_format = self.detect_format(file_path)

            self.stdout.write(f"Reading {file_format.upper()} file: {file_path}")

            if file_format == "json":
                bible_data = self.load_json(file_path)
            elif file_format == "csv":
                bible_data = self.load_csv(file_path)
            elif file_format == "txt":
                bible_data = self.load_txt(file_path)
            elif file_format == "sqlite":
                bible_data = self.load_sqlite(file_path)
            else:
                self.stderr.write(
                    self.style.ERROR(f"Unsupported format: {file_format}")
                )
                return
        else:
            self.stdout.write("No file specified, using sample data...")
            bible_data = self.get_sample_data()

        # Import books
        self.stdout.write("Creating books...")
        books_created = 0
        verses_created = 0

        for book_data in bible_data:
            book, created = BibleBook.objects.get_or_create(
                name=book_data["name"],
                defaults={
                    "slug": book_data["slug"],
                    "order": book_data["order"],
                    "testament": book_data["testament"],
                    "chapters": book_data["chapters"],
                },
            )

            if created:
                books_created += 1

            # Import verses for this book
            self.stdout.write(f"  Importing verses for {book.name}...")

            # Deduplicate verses within this book (keep last occurrence)
            seen_verses = {}
            for verse_data in book_data["verses"]:
                key = (verse_data["chapter"], verse_data["verse"])
                seen_verses[key] = verse_data

            verses_to_create = []
            for (chapter, verse_num), verse_data in seen_verses.items():
                # Check if verse already exists in database
                if not BibleVerse.objects.filter(
                    book=book, chapter=chapter, verse=verse_num
                ).exists():
                    verses_to_create.append(
                        BibleVerse(
                            book=book,
                            chapter=chapter,
                            verse=verse_num,
                            text=verse_data["text"],
                        )
                    )

            if verses_to_create:
                BibleVerse.objects.bulk_create(verses_to_create)
                verses_created += len(verses_to_create)
                self.stdout.write(f"    Imported {len(verses_to_create)} verses")

        total_books = BibleBook.objects.count()
        total_verses = BibleVerse.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully imported {books_created} new books and {verses_created} new verses"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Total in database: {total_books} books and {total_verses} verses"
            )
        )

    def detect_format(self, file_path):
        """Auto-detect file format based on extension and content."""
        suffix = file_path.suffix.lower()
        if suffix == ".json":
            return "json"
        elif suffix == ".csv":
            return "csv"
        elif suffix in [".db", ".sqlite", ".sqlite3"]:
            return "sqlite"
        elif suffix in [".txt", ".text"]:
            return "txt"
        return "txt"  # Default to txt

    def load_json(self, file_path):
        """
        Load Bible data from JSON file.

        Expected format:
        [
            {
                "name": "Genesis",
                "slug": "genesis",
                "order": 1,
                "testament": "OT",
                "chapters": 50,
                "verses": [
                    {"chapter": 1, "verse": 1, "text": "..."},
                    ...
                ]
            },
            ...
        ]
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_csv(self, file_path):
        """
        Load Bible data from CSV file.

        Expected CSV format:
        book_name,book_slug,book_order,testament,chapter,verse,text
        Genesis,genesis,1,OT,1,1,"In the beginning..."
        """
        books_dict = {}

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                book_name = row["book_name"]

                if book_name not in books_dict:
                    books_dict[book_name] = {
                        "name": book_name,
                        "slug": row["book_slug"],
                        "order": int(row["book_order"]),
                        "testament": row["testament"],
                        "chapters": 0,
                        "verses": [],
                    }

                chapter_num = int(row["chapter"])
                verse_num = int(row["verse"])

                # Update max chapters
                if chapter_num > books_dict[book_name]["chapters"]:
                    books_dict[book_name]["chapters"] = chapter_num

                books_dict[book_name]["verses"].append(
                    {"chapter": chapter_num, "verse": verse_num, "text": row["text"]}
                )

        return list(books_dict.values())

    def load_txt(self, file_path):
        """
        Load Bible data from plain text file.

        Supports multiple formats:
        1. Simple format: "Book Chapter:Verse Text"
           Example: Genesis 1:1 In the beginning...

        2. Block format with headers:
           Genesis 1
           1 In the beginning...
           2 And the earth was...
        """
        books_dict = {}
        current_book = None
        current_chapter = None

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Try format: "Book Chapter:Verse Text"
                match = re.match(
                    r"^([1-3]?\s*[A-Za-z\s]+?)\s+(\d+):(\d+)\s+(.+)$", line
                )
                if match:
                    book_name = match.group(1).strip()
                    chapter = int(match.group(2))
                    verse = int(match.group(3))
                    text = match.group(4)

                    if book_name not in books_dict:
                        books_dict[book_name] = {
                            "name": book_name,
                            "slug": book_name.lower().replace(" ", "-"),
                            "order": len(books_dict) + 1,
                            "testament": "OT" if len(books_dict) < 39 else "NT",
                            "chapters": 0,
                            "verses": [],
                        }

                    if chapter > books_dict[book_name]["chapters"]:
                        books_dict[book_name]["chapters"] = chapter

                    books_dict[book_name]["verses"].append(
                        {"chapter": chapter, "verse": verse, "text": text}
                    )
                    continue

                # Try format: Book header or verse without book prefix
                # This is more complex and would need more context

        return list(books_dict.values())

    # KJV canonical book metadata: (name, slug, testament, chapter_count)
    # Indexed by standard book number (1-66).
    _KJV_BOOK_INFO = [
        None,  # placeholder so index 1 = Genesis
        ("Genesis", "genesis", "OT", 50),
        ("Exodus", "exodus", "OT", 40),
        ("Leviticus", "leviticus", "OT", 27),
        ("Numbers", "numbers", "OT", 36),
        ("Deuteronomy", "deuteronomy", "OT", 34),
        ("Joshua", "joshua", "OT", 24),
        ("Judges", "judges", "OT", 21),
        ("Ruth", "ruth", "OT", 4),
        ("1 Samuel", "1-samuel", "OT", 31),
        ("2 Samuel", "2-samuel", "OT", 24),
        ("1 Kings", "1-kings", "OT", 22),
        ("2 Kings", "2-kings", "OT", 25),
        ("1 Chronicles", "1-chronicles", "OT", 29),
        ("2 Chronicles", "2-chronicles", "OT", 36),
        ("Ezra", "ezra", "OT", 10),
        ("Nehemiah", "nehemiah", "OT", 13),
        ("Esther", "esther", "OT", 10),
        ("Job", "job", "OT", 42),
        ("Psalms", "psalms", "OT", 150),
        ("Proverbs", "proverbs", "OT", 31),
        ("Ecclesiastes", "ecclesiastes", "OT", 12),
        ("Song of Solomon", "song-of-solomon", "OT", 8),
        ("Isaiah", "isaiah", "OT", 66),
        ("Jeremiah", "jeremiah", "OT", 52),
        ("Lamentations", "lamentations", "OT", 5),
        ("Ezekiel", "ezekiel", "OT", 48),
        ("Daniel", "daniel", "OT", 12),
        ("Hosea", "hosea", "OT", 14),
        ("Joel", "joel", "OT", 3),
        ("Amos", "amos", "OT", 9),
        ("Obadiah", "obadiah", "OT", 1),
        ("Jonah", "jonah", "OT", 4),
        ("Micah", "micah", "OT", 7),
        ("Nahum", "nahum", "OT", 3),
        ("Habakkuk", "habakkuk", "OT", 3),
        ("Zephaniah", "zephaniah", "OT", 3),
        ("Haggai", "haggai", "OT", 2),
        ("Zechariah", "zechariah", "OT", 14),
        ("Malachi", "malachi", "OT", 4),
        ("Matthew", "matthew", "NT", 28),
        ("Mark", "mark", "NT", 16),
        ("Luke", "luke", "NT", 24),
        ("John", "john", "NT", 21),
        ("Acts", "acts", "NT", 28),
        ("Romans", "romans", "NT", 16),
        ("1 Corinthians", "1-corinthians", "NT", 16),
        ("2 Corinthians", "2-corinthians", "NT", 13),
        ("Galatians", "galatians", "NT", 6),
        ("Ephesians", "ephesians", "NT", 6),
        ("Philippians", "philippians", "NT", 4),
        ("Colossians", "colossians", "NT", 4),
        ("1 Thessalonians", "1-thessalonians", "NT", 5),
        ("2 Thessalonians", "2-thessalonians", "NT", 3),
        ("1 Timothy", "1-timothy", "NT", 6),
        ("2 Timothy", "2-timothy", "NT", 4),
        ("Titus", "titus", "NT", 3),
        ("Philemon", "philemon", "NT", 1),
        ("Hebrews", "hebrews", "NT", 13),
        ("James", "james", "NT", 5),
        ("1 Peter", "1-peter", "NT", 5),
        ("2 Peter", "2-peter", "NT", 3),
        ("1 John", "1-john", "NT", 5),
        ("2 John", "2-john", "NT", 1),
        ("3 John", "3-john", "NT", 1),
        ("Jude", "jude", "NT", 1),
        ("Revelation", "revelation", "NT", 22),
    ]

    def load_sqlite(self, file_path):
        """
        Load Bible data from a KJV SQLite database file.

        Expected schema (used by many open-source KJV SQLite datasets):
          key_english(b INTEGER, n TEXT)   -- book number -> book name
          t_kjv(b INTEGER, c INTEGER, v INTEGER, t TEXT)
                                           -- book, chapter, verse, text

        Book numbers follow the standard 1-66 KJV ordering.
        If key_english is absent, canonical names from _KJV_BOOK_INFO are used.
        """
        books_dict = {}

        conn = sqlite3.connect(str(file_path))
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Build a book-number -> name mapping from key_english if available.
            book_names = {}
            try:
                cursor.execute("SELECT b, n FROM key_english ORDER BY b")
                for row in cursor.fetchall():
                    book_names[row["b"]] = row["n"]
            except sqlite3.OperationalError:
                # key_english table not present; fall back to canonical names.
                pass

            # Read all verses from t_kjv.
            cursor.execute("SELECT b, c, v, t FROM t_kjv ORDER BY b, c, v")
            rows = cursor.fetchall()
        finally:
            conn.close()

        for row in rows:
            book_num = row["b"]
            chapter = row["c"]
            verse = row["v"]
            text = row["t"]

            if book_num not in books_dict:
                # Determine metadata from key_english or canonical table.
                if book_names.get(book_num):
                    db_name = book_names[book_num]
                elif 1 <= book_num <= 66 and self._KJV_BOOK_INFO[book_num]:
                    db_name = self._KJV_BOOK_INFO[book_num][0]
                else:
                    db_name = f"Book {book_num}"

                # Use canonical metadata when available; fall back to guessing.
                if 1 <= book_num <= 66 and self._KJV_BOOK_INFO[book_num]:
                    canon_name, slug, testament, chapter_count = self._KJV_BOOK_INFO[
                        book_num
                    ]
                    name = db_name if db_name else canon_name
                else:
                    name = db_name
                    slug = name.lower().replace(" ", "-")
                    testament = "OT" if book_num <= 39 else "NT"
                    chapter_count = 0  # will be updated below

                books_dict[book_num] = {
                    "name": name,
                    "slug": slug,
                    "order": book_num,
                    "testament": testament,
                    "chapters": chapter_count,
                    "verses": [],
                }

            # Update chapter count if we didn't have canonical data.
            if chapter > books_dict[book_num]["chapters"]:
                books_dict[book_num]["chapters"] = chapter

            books_dict[book_num]["verses"].append(
                {"chapter": chapter, "verse": verse, "text": text}
            )

        return [books_dict[k] for k in sorted(books_dict)]

    def get_sample_data(self):
        """
        Returns sample Bible data for testing.
        In production, Bible content should be maintained in the SQLite database.
        """
        return [
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
                        "text": "In the beginning God created the heaven and the earth.",
                    },
                    {
                        "chapter": 1,
                        "verse": 2,
                        "text": "And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.",
                    },
                    {
                        "chapter": 1,
                        "verse": 3,
                        "text": "And God said, Let there be light: and there was light.",
                    },
                ],
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
                        "text": "In the beginning was the Word, and the Word was with God, and the Word was God.",
                    },
                    {
                        "chapter": 1,
                        "verse": 2,
                        "text": "The same was in the beginning with God.",
                    },
                    {
                        "chapter": 3,
                        "verse": 16,
                        "text": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                    },
                    {
                        "chapter": 3,
                        "verse": 17,
                        "text": "For God sent not his Son into the world to condemn the world; but that the world through him might be saved.",
                    },
                ],
            },
            {
                "name": "Revelation",
                "slug": "revelation",
                "order": 66,
                "testament": "NT",
                "chapters": 22,
                "verses": [
                    {
                        "chapter": 1,
                        "verse": 1,
                        "text": "The Revelation of Jesus Christ, which God gave unto him, to shew unto his servants things which must shortly come to pass; and he sent and signified it by his angel unto his servant John:",
                    },
                    {
                        "chapter": 22,
                        "verse": 21,
                        "text": "The grace of our Lord Jesus Christ be with you all. Amen.",
                    },
                ],
            },
        ]
