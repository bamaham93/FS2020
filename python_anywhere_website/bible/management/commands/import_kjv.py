from django.core.management.base import BaseCommand, CommandError
from bible.models import BibleBook, BibleVerse
import json
import csv
import re
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path


class Command(BaseCommand):
    help = "Import KJV Bible data into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the data file (JSON, CSV, TXT, SQLite, or XML)",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["json", "csv", "txt", "sqlite", "xml", "auto"],
            default="auto",
            help="Format of the input file (auto-detect if not specified)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing Bible data before importing",
        )
        parser.add_argument(
            "--sample",
            action="store_true",
            help="Use the small built-in sample dataset when no file is specified",
        )

    def handle(self, *args, **options):
        self.stdout.write("Importing KJV Bible data...")

        # Clear existing data if requested
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            BibleVerse.objects.all().delete()
            BibleBook.objects.all().delete()

        # Load data from file, bundled XML, or sample data.
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
            elif file_format == "xml":
                bible_data = self.load_xml(file_path)
            else:
                self.stderr.write(
                    self.style.ERROR(f"Unsupported format: {file_format}")
                )
                return
        else:
            file_path = self.find_default_xml_file()
            if file_path:
                self.stdout.write(f"No file specified, using XML file: {file_path}")
                bible_data = self.load_xml(file_path)
            elif options["sample"]:
                self.stdout.write("No XML file found, using sample data...")
                bible_data = self.get_sample_data()
            else:
                raise CommandError(
                    "No Bible data file specified and no bundled XML file was found."
                )

        # Import books
        self.stdout.write("Creating books...")
        books_created = 0
        verses_created = 0

        for book_data in bible_data:
            book, created = BibleBook.objects.update_or_create(
                order=book_data["order"],
                defaults={
                    "name": book_data["name"],
                    "slug": book_data["slug"],
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

            existing_verses = {
                (verse.chapter, verse.verse): verse
                for verse in BibleVerse.objects.filter(book=book)
            }
            verses_to_create = []
            verses_to_update = []
            for (chapter, verse_num), verse_data in seen_verses.items():
                existing_verse = existing_verses.get((chapter, verse_num))
                if existing_verse:
                    if existing_verse.text != verse_data["text"]:
                        existing_verse.text = verse_data["text"]
                        verses_to_update.append(existing_verse)
                else:
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
            if verses_to_update:
                BibleVerse.objects.bulk_update(verses_to_update, ["text"])
                self.stdout.write(f"    Updated {len(verses_to_update)} verses")

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
        elif suffix == ".xml":
            return "xml"
        elif suffix in [".txt", ".text"]:
            return "txt"
        return "txt"  # Default to txt

    def find_default_xml_file(self):
        """Find a bundled Bible XML file without depending on a hard-coded name."""
        command_path = Path(__file__).resolve()
        app_root = command_path.parents[3]
        project_root = command_path.parents[4]
        candidates = [
            app_root / "bible" / "data",
            app_root / "data",
            app_root,
            project_root,
        ]

        for candidate in candidates:
            if not candidate.exists():
                continue
            xml_files = sorted(
                path
                for path in candidate.glob("*.xml")
                if ".idea" not in path.parts and path.is_file()
            )
            if xml_files:
                return xml_files[0]

        return None

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

    def load_xml(self, file_path):
        """
        Load Bible data from XML.

        Supports common KJV layouts, including Zefania-style:
          BIBLEBOOK -> CHAPTER -> VERS
        simple XML:
          bible -> book -> chapter -> verse
        and OSIS-style:
          div(type=book) -> chapter -> verse
        """
        root = ET.parse(file_path).getroot()
        books = self.load_simple_xml(root)
        if books:
            return books
        books = self.load_zefania_xml(root)
        if books:
            return books
        books = self.load_osis_xml(root)
        if books:
            return books
        raise ValueError(f"Unsupported Bible XML structure: {file_path}")

    def load_simple_xml(self, root):
        books = []
        if self.xml_tag(root) != "bible":
            return books

        for book_element in root:
            if self.xml_tag(book_element) != "book":
                continue

            book_num = self.book_order_from_xml_num(book_element.attrib.get("num"))
            if book_num is None:
                book_num = len(books) + 1
            book_info = self.book_info_for_order(book_num)

            verses = []
            max_chapter = 0
            for chapter_element in book_element:
                if self.xml_tag(chapter_element) != "chapter":
                    continue
                chapter = self.xml_int_attr(chapter_element, "num", "number")
                if chapter is None:
                    continue
                max_chapter = max(max_chapter, chapter)

                for verse_element in chapter_element:
                    if self.xml_tag(verse_element) != "verse":
                        continue
                    verse = self.xml_int_attr(verse_element, "num", "number")
                    if verse is None:
                        continue
                    text = " ".join("".join(verse_element.itertext()).split())
                    verses.append({"chapter": chapter, "verse": verse, "text": text})

            books.append(
                {
                    "name": book_info["name"],
                    "slug": book_info["slug"],
                    "order": book_num,
                    "testament": book_info["testament"],
                    "chapters": book_info["chapters"] or max_chapter,
                    "verses": verses,
                }
            )

        return books

    def load_zefania_xml(self, root):
        books = []
        for book_element in root.iter():
            if self.xml_tag(book_element) != "BIBLEBOOK":
                continue

            book_num = self.xml_int_attr(book_element, "bnumber", "bnum", "number")
            if book_num is None:
                book_num = len(books) + 1
            book_info = self.book_info_for_order(book_num)
            name = (
                book_element.attrib.get("bname")
                or book_element.attrib.get("name")
                or book_info["name"]
            )

            verses = []
            max_chapter = 0
            for chapter_element in book_element:
                if self.xml_tag(chapter_element) != "CHAPTER":
                    continue
                chapter = self.xml_int_attr(chapter_element, "cnumber", "number")
                if chapter is None:
                    continue
                max_chapter = max(max_chapter, chapter)

                for verse_element in chapter_element:
                    if self.xml_tag(verse_element) != "VERS":
                        continue
                    verse = self.xml_int_attr(verse_element, "vnumber", "number")
                    if verse is None:
                        continue
                    text = " ".join("".join(verse_element.itertext()).split())
                    verses.append({"chapter": chapter, "verse": verse, "text": text})

            books.append(
                {
                    "name": name,
                    "slug": book_info["slug"],
                    "order": book_num,
                    "testament": book_info["testament"],
                    "chapters": book_info["chapters"] or max_chapter,
                    "verses": verses,
                }
            )

        return books

    def load_osis_xml(self, root):
        books = []
        for book_element in root.iter():
            if self.xml_tag(book_element) != "div":
                continue
            if book_element.attrib.get("type") != "book":
                continue

            book_num = len(books) + 1
            book_info = self.book_info_for_order(book_num)
            name = book_element.attrib.get("canonicalTitle") or book_info["name"]

            verses = []
            max_chapter = 0
            for chapter_element in book_element.iter():
                if self.xml_tag(chapter_element) != "chapter":
                    continue
                chapter = self.chapter_from_osis_id(chapter_element.attrib.get("osisID"))
                if chapter is None:
                    continue
                max_chapter = max(max_chapter, chapter)

                for verse_element in chapter_element:
                    if self.xml_tag(verse_element) != "verse":
                        continue
                    verse = self.verse_from_osis_id(verse_element.attrib.get("osisID"))
                    if verse is None:
                        continue
                    text = " ".join("".join(verse_element.itertext()).split())
                    verses.append({"chapter": chapter, "verse": verse, "text": text})

            books.append(
                {
                    "name": name,
                    "slug": book_info["slug"],
                    "order": book_num,
                    "testament": book_info["testament"],
                    "chapters": book_info["chapters"] or max_chapter,
                    "verses": verses,
                }
            )

        return books

    def book_info_for_order(self, book_num):
        if 1 <= book_num <= 66 and self._KJV_BOOK_INFO[book_num]:
            name, slug, testament, chapters = self._KJV_BOOK_INFO[book_num]
            return {
                "name": name,
                "slug": slug,
                "testament": testament,
                "chapters": chapters,
            }
        return {
            "name": f"Book {book_num}",
            "slug": f"book-{book_num}",
            "testament": "OT" if book_num <= 39 else "NT",
            "chapters": 0,
        }

    def xml_tag(self, element):
        return element.tag.rsplit("}", 1)[-1]

    def xml_int_attr(self, element, *names):
        for name in names:
            value = element.attrib.get(name)
            if value and value.isdigit():
                return int(value)
        return None

    def book_order_from_xml_num(self, xml_num):
        if not xml_num:
            return None
        if xml_num.isdigit():
            return int(xml_num)

        xml_books = [
            "Gen",
            "Exod",
            "Lev",
            "Num",
            "Deut",
            "Josh",
            "Judg",
            "Ruth",
            "1Sam",
            "2Sam",
            "1Kgs",
            "2Kgs",
            "1Chr",
            "2Chr",
            "Ezra",
            "Neh",
            "Esth",
            "Job",
            "Ps",
            "Prov",
            "Eccl",
            "Song",
            "Isa",
            "Jer",
            "Lam",
            "Ezek",
            "Dan",
            "Hos",
            "Joel",
            "Amos",
            "Obad",
            "Jonah",
            "Mic",
            "Nah",
            "Hab",
            "Zeph",
            "Hag",
            "Zech",
            "Mal",
            "Matt",
            "Mark",
            "Luke",
            "John",
            "Acts",
            "Rom",
            "1Cor",
            "2Cor",
            "Gal",
            "Eph",
            "Phil",
            "Col",
            "1Thess",
            "2Thess",
            "1Tim",
            "2Tim",
            "Titus",
            "Phlm",
            "Heb",
            "Jas",
            "1Pet",
            "2Pet",
            "1John",
            "2John",
            "3John",
            "Jude",
            "Rev",
        ]
        try:
            return xml_books.index(xml_num) + 1
        except ValueError:
            return None

    def chapter_from_osis_id(self, osis_id):
        if not osis_id:
            return None
        parts = osis_id.split(".")
        if len(parts) >= 2 and parts[-1].isdigit():
            return int(parts[-1])
        return None

    def verse_from_osis_id(self, osis_id):
        if not osis_id:
            return None
        parts = osis_id.split(".")
        if len(parts) >= 3 and parts[-1].isdigit():
            return int(parts[-1])
        return None

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
                    name = db_name or canon_name
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

        return [books_dict[k] for k in sorted(books_dict.keys())]

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
