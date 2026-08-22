from django.test import TestCase, Client
from django.urls import reverse
from bible.models import BibleBook, BibleVerse
import sqlite3
import tempfile
import os


class BibleBookModelTest(TestCase):
    def setUp(self):
        BibleBook.objects.all().delete()
        self.book = BibleBook.objects.create(
            name="John", slug="john", order=43, testament="NT", chapters=21
        )

    def test_book_creation(self):
        self.assertEqual(self.book.name, "John")
        self.assertEqual(self.book.slug, "john")
        self.assertEqual(str(self.book), "John")

    def test_book_ordering(self):
        genesis = BibleBook.objects.create(
            name="Genesis", slug="genesis", order=1, testament="OT", chapters=50
        )
        books = list(BibleBook.objects.all())
        self.assertEqual(books[0], genesis)
        self.assertEqual(books[1], self.book)


class BibleVerseModelTest(TestCase):
    def setUp(self):
        BibleBook.objects.all().delete()
        self.book = BibleBook.objects.create(
            name="John", slug="john", order=43, testament="NT", chapters=21
        )
        self.verse = BibleVerse.objects.create(
            book=self.book, chapter=3, verse=16, text="For God so loved the world..."
        )

    def test_verse_creation(self):
        self.assertEqual(self.verse.chapter, 3)
        self.assertEqual(self.verse.verse, 16)
        self.assertEqual(str(self.verse), "John 3:16")

    def test_verse_unique_constraint(self):
        with self.assertRaises(Exception):
            BibleVerse.objects.create(
                book=self.book, chapter=3, verse=16, text="Duplicate verse"
            )


class BibleViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        BibleBook.objects.all().delete()
        self.book = BibleBook.objects.create(
            name="John", slug="john", order=43, testament="NT", chapters=21
        )
        self.verse1 = BibleVerse.objects.create(
            book=self.book, chapter=3, verse=16, text="For God so loved the world..."
        )
        self.verse2 = BibleVerse.objects.create(
            book=self.book, chapter=3, verse=17, text="For God sent not his Son..."
        )

    def test_book_list_view(self):
        response = self.client.get(reverse("bible:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John")

    def test_multiple_books_displayed(self):
        """Integration test: Verify multiple books are displayed on the home page."""
        # Delete the book created in setUp to avoid conflicts
        BibleBook.objects.all().delete()

        books = [
            ("Genesis", "genesis", 1, "OT", 50),
            ("1 Samuel", "1-samuel", 9, "OT", 31),
            ("2 Samuel", "2-samuel", 10, "OT", 24),
            ("1 Kings", "1-kings", 11, "OT", 22),
            ("2 Kings", "2-kings", 12, "OT", 25),
            ("1 Chronicles", "1-chronicles", 13, "OT", 29),
            ("2 Chronicles", "2-chronicles", 14, "OT", 36),
            ("John", "john", 43, "NT", 21),
            ("Revelation", "revelation", 66, "NT", 22),
        ]

        for book_name, slug, order, testament, chapters in books:
            BibleBook.objects.create(
                name=book_name,
                slug=slug,
                order=order,
                testament=testament,
                chapters=chapters,
            )

        self.assertEqual(BibleBook.objects.count(), len(books))

        response = self.client.get(reverse("bible:index"))
        self.assertEqual(response.status_code, 200)

        for book_name, *_ in books:
            with self.subTest(book=book_name):
                self.assertContains(response, book_name)

        self.assertContains(response, "Old Testament")
        self.assertContains(response, "New Testament")

        self.assertContains(response, "1 Samuel")
        self.assertContains(response, "2 Samuel")
        self.assertContains(response, "1 Kings")
        self.assertContains(response, "2 Kings")
        self.assertContains(response, "1 Chronicles")
        self.assertContains(response, "2 Chronicles")

    def test_chapter_list_view(self):
        response = self.client.get(reverse("bible:chapter_list", args=["john"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John")
        self.assertContains(response, reverse("bible:chapter_reader", args=["john", 1]))

    def test_chapter_reader_view(self):
        response = self.client.get(reverse("bible:chapter_reader", args=["john", 3]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "For God so loved the world")
        self.assertContains(response, "v16")

    def test_invalid_chapter(self):
        response = self.client.get(reverse("bible:chapter_reader", args=["john", 999]))
        self.assertEqual(response.status_code, 404)

    def test_continuous_reader_view(self):
        response = self.client.get(reverse("bible:continuous_reader"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Continuous KJV Reader")
        self.assertContains(response, 'data-book="john"')
        self.assertContains(response, 'data-chapter="1"')

    def test_continuous_reader_hyperlink_targets(self):
        response = self.client.get(reverse("bible:continuous_reader"))
        self.assertEqual(response.status_code, 200)
        expected_url = reverse("bible:continuous_reader_chapter", args=["john", 1])
        self.assertContains(response, f'href="{expected_url}#chapter-john-1"')

    def test_continuous_reader_accepts_book_chapter_url(self):
        response = self.client.get(
            reverse("bible:continuous_reader_chapter", args=["john", 3])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "chapter: 3")
        self.assertContains(response, "chapterCount: 21")
        self.assertContains(response, '<details class="book-item" open>')

    def test_continuous_reader_accepts_book_chapter_query_params(self):
        response = self.client.get(
            reverse("bible:continuous_reader"),
            {"book": "john", "chapter": "3"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "chapter: 3")

    def test_seed_kjv_books_backfills_all_canonical_books(self):
        """The deployment migration should repair databases with sample data only."""
        import importlib
        from django.apps import apps

        migration = importlib.import_module("bible.migrations.0002_seed_kjv_books")

        BibleBook.objects.exclude(slug__in=["genesis", "john", "revelation"]).delete()

        migration.seed_kjv_books(apps, None)

        self.assertEqual(BibleBook.objects.count(), 66)
        self.assertEqual(BibleBook.objects.filter(testament="OT").count(), 39)
        self.assertEqual(BibleBook.objects.filter(testament="NT").count(), 27)
        self.assertEqual(BibleBook.objects.get(order=1).slug, "genesis")
        self.assertEqual(BibleBook.objects.get(order=66).slug, "revelation")


class BibleAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        BibleBook.objects.all().delete()
        self.book = BibleBook.objects.create(
            name="John", slug="john", order=43, testament="NT", chapters=21
        )
        self.verse = BibleVerse.objects.create(
            book=self.book, chapter=3, verse=16, text="For God so loved the world..."
        )

    def test_api_books(self):
        response = self.client.get("/api/v1/bible/books")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("books", data)
        self.assertEqual(len(data["books"]), 1)
        self.assertEqual(data["books"][0]["name"], "John")

    def test_api_chapter(self):
        response = self.client.get("/api/v1/bible/books/john/chapters/3")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["chapter"], 3)
        self.assertEqual(len(data["verses"]), 1)
        self.assertEqual(data["verses"][0]["verse"], 16)

    def test_api_passage(self):
        response = self.client.get("/api/v1/bible/passage?ref=John+3:16")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["chapter"], 3)
        self.assertEqual(len(data["verses"]), 1)
        self.assertEqual(data["verses"][0]["verse"], 16)

    def test_api_passage_invalid(self):
        response = self.client.get("/api/v1/bible/passage?ref=Invalid")
        self.assertEqual(response.status_code, 400)

    def test_api_rate_limit_headers(self):
        response = self.client.get("/api/v1/bible/books")
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-RateLimit-Limit", response)
        self.assertIn("X-RateLimit-Remaining", response)
        self.assertEqual(response["X-RateLimit-Limit"], "100")


class BibleAdminActionTest(TestCase):
    """Tests for the admin import_kjv_action."""

    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Create a staff user
        self.staff_user = User.objects.create_user(
            username="staffuser",
            password="testpass123",
            is_staff=True,
            is_superuser=True,
        )

        # Create a non-staff user
        self.regular_user = User.objects.create_user(
            username="regularuser", password="testpass123", is_staff=False
        )

        # Create a test book
        BibleBook.objects.all().delete()
        self.book = BibleBook.objects.create(
            name="Test Book", slug="test-book", order=1, testament="OT", chapters=1
        )

    def test_import_action_exists(self):
        """Test that the import action is registered."""
        from bible.admin import BibleBookAdmin, import_kjv_action

        admin_instance = BibleBookAdmin(BibleBook, None)
        self.assertIn(import_kjv_action, admin_instance.actions)

    def test_import_action_attributes(self):
        """Test that the import action has correct attributes."""
        from bible.admin import import_kjv_action

        self.assertEqual(import_kjv_action.short_description, "Import KJV Bible")
        self.assertEqual(import_kjv_action.allowed_permissions, ("change",))

    def test_import_action_staff_user(self):
        """Test that staff users can trigger the import."""
        from bible.admin import BibleBookAdmin, import_kjv_action
        from django.contrib import messages as django_messages
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.test import RequestFactory
        from unittest.mock import patch, MagicMock

        factory = RequestFactory()
        request = factory.post("/admin/bible/biblebook/")
        request.user = self.staff_user

        # Set up messages framework
        setattr(request, "session", "session")
        messages_storage = FallbackStorage(request)
        setattr(request, "_messages", messages_storage)

        admin_instance = BibleBookAdmin(BibleBook, None)
        queryset = BibleBook.objects.filter(pk=self.book.pk)

        # Mock threading.Thread to prevent actual background execution
        with patch("bible.admin.threading.Thread") as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            # Call the action
            import_kjv_action(admin_instance, request, queryset)

            # Verify thread was created and started
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()

        # Check that success message was added
        messages_list = list(django_messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn("KJV import has been started", str(messages_list[0]))

    def test_import_action_non_staff_user(self):
        """Test that non-staff users cannot trigger the import."""
        from bible.admin import BibleBookAdmin, import_kjv_action
        from django.contrib import messages as django_messages
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.post("/admin/bible/biblebook/")
        request.user = self.regular_user

        # Set up messages framework
        setattr(request, "session", "session")
        messages_storage = FallbackStorage(request)
        setattr(request, "_messages", messages_storage)

        admin_instance = BibleBookAdmin(BibleBook, None)
        queryset = BibleBook.objects.filter(pk=self.book.pk)

        # Call the action
        import_kjv_action(admin_instance, request, queryset)

        # Check that error message was added
        messages_list = list(django_messages.get_messages(request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn("Only staff users", str(messages_list[0]))

    def test_run_import_kjv_function(self):
        """Test the _run_import_kjv helper function."""
        from bible.admin import _run_import_kjv
        from unittest.mock import patch

        # Test successful import
        with patch("bible.admin.call_command") as mock_call_command:
            _run_import_kjv("testuser")
            mock_call_command.assert_called_once_with("import_kjv", clear=True)

        # Test exception handling
        with patch("bible.admin.call_command") as mock_call_command:
            mock_call_command.side_effect = Exception("Test error")
            # Should not raise, just log
            _run_import_kjv("testuser")


class ImportKJVSQLiteTest(TestCase):
    """Tests for import_kjv management command's sqlite format support."""

    def _make_kjv_db(self, path, rows, include_key_english=True):
        """Create a minimal KJV SQLite database at *path* with *rows*.

        rows is a list of (b, c, v, t) tuples.
        """
        conn = sqlite3.connect(path)
        try:
            conn.execute("CREATE TABLE t_kjv (b INTEGER, c INTEGER, v INTEGER, t TEXT)")
            conn.executemany("INSERT INTO t_kjv VALUES (?,?,?,?)", rows)
            if include_key_english:
                conn.execute("CREATE TABLE key_english (b INTEGER PRIMARY KEY, n TEXT)")
                # Insert names only for the books that appear in rows
                book_nums = sorted({r[0] for r in rows})
                from bible.management.commands.import_kjv import Command

                for b in book_nums:
                    if 1 <= b <= 66 and Command._KJV_BOOK_INFO[b]:
                        name = Command._KJV_BOOK_INFO[b][0]
                        conn.execute("INSERT INTO key_english VALUES (?,?)", (b, name))
            conn.commit()
        finally:
            conn.close()

    def test_load_sqlite_basic(self):
        """load_sqlite returns correct book/verse structure."""
        from bible.management.commands.import_kjv import Command
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "kjv.db")
            self._make_kjv_db(
                db_path,
                [
                    (1, 1, 1, "In the beginning God created the heaven and the earth."),
                    (1, 1, 2, "And the earth was without form, and void."),
                    (43, 3, 16, "For God so loved the world..."),
                ],
            )
            cmd = Command()
            result = cmd.load_sqlite(Path(db_path))

        # Should return two books in order
        self.assertEqual(len(result), 2)
        genesis = result[0]
        john = result[1]

        self.assertEqual(genesis["name"], "Genesis")
        self.assertEqual(genesis["slug"], "genesis")
        self.assertEqual(genesis["order"], 1)
        self.assertEqual(genesis["testament"], "OT")
        self.assertEqual(genesis["chapters"], 50)
        self.assertEqual(len(genesis["verses"]), 2)
        self.assertEqual(
            genesis["verses"][0]["text"],
            "In the beginning God created the heaven and the earth.",
        )

        self.assertEqual(john["name"], "John")
        self.assertEqual(john["slug"], "john")
        self.assertEqual(john["order"], 43)
        self.assertEqual(john["testament"], "NT")
        self.assertEqual(john["chapters"], 21)
        self.assertEqual(len(john["verses"]), 1)
        self.assertEqual(john["verses"][0]["verse"], 16)

    def test_load_sqlite_without_key_english(self):
        """load_sqlite falls back to canonical names when key_english is absent."""
        from bible.management.commands.import_kjv import Command
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "kjv_no_key.db")
            self._make_kjv_db(
                db_path,
                [(66, 22, 21, "The grace of our Lord Jesus Christ be with you all.")],
                include_key_english=False,
            )
            cmd = Command()
            result = cmd.load_sqlite(Path(db_path))

        self.assertEqual(len(result), 1)
        revelation = result[0]
        self.assertEqual(revelation["name"], "Revelation")
        self.assertEqual(revelation["testament"], "NT")

    def test_detect_format_sqlite_extensions(self):
        """detect_format recognises .db, .sqlite, and .sqlite3 as sqlite."""
        from bible.management.commands.import_kjv import Command
        from pathlib import Path

        cmd = Command()
        for ext in [".db", ".sqlite", ".sqlite3"]:
            with self.subTest(ext=ext):
                self.assertEqual(cmd.detect_format(Path(f"kjv{ext}")), "sqlite")

    def test_detect_format_xml_extension(self):
        """detect_format recognises XML Bible files."""
        from bible.management.commands.import_kjv import Command
        from pathlib import Path

        cmd = Command()
        self.assertEqual(cmd.detect_format(Path("kjv.xml")), "xml")

    def test_load_xml_zefania_format(self):
        """load_xml parses bundled Zefania-style KJV XML files."""
        from bible.management.commands.import_kjv import Command
        from pathlib import Path

        xml = """<?xml version="1.0" encoding="utf-8"?>
<XMLBIBLE>
  <BIBLEBOOK bnumber="1" bname="Genesis">
    <CHAPTER cnumber="1">
      <VERS vnumber="1">In the beginning God created the heaven and the earth.</VERS>
      <VERS vnumber="2">And the earth was without form, and void.</VERS>
    </CHAPTER>
  </BIBLEBOOK>
  <BIBLEBOOK bnumber="43" bname="John">
    <CHAPTER cnumber="3">
      <VERS vnumber="16">For God so loved the world.</VERS>
    </CHAPTER>
  </BIBLEBOOK>
</XMLBIBLE>
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = os.path.join(tmpdir, "kjv.xml")
            with open(xml_path, "w", encoding="utf-8") as f:
                f.write(xml)
            result = Command().load_xml(Path(xml_path))

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Genesis")
        self.assertEqual(result[0]["slug"], "genesis")
        self.assertEqual(result[0]["chapters"], 50)
        self.assertEqual(len(result[0]["verses"]), 2)
        self.assertEqual(result[1]["name"], "John")
        self.assertEqual(result[1]["order"], 43)
        self.assertEqual(result[1]["verses"][0]["chapter"], 3)
        self.assertEqual(result[1]["verses"][0]["verse"], 16)

    def test_load_xml_simple_open_source_bible_data_format(self):
        """load_xml parses the simple XML format from open-source-bible-data."""
        from bible.management.commands.import_kjv import Command
        from pathlib import Path

        xml = """<bible abbrev="KJV" name="King James Bible">
<book num="Gen">
  <chapter num="1">
    <verse num="1">In the beginning God created the heaven and the earth.</verse>
    <verse num="2">And the earth was without form, and void; and darkness <i>was</i> upon the face of the deep.</verse>
  </chapter>
</book>
<book num="John">
  <chapter num="3">
    <verse num="16">For God so loved the world.</verse>
  </chapter>
</book>
</bible>
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = os.path.join(tmpdir, "kjv.xml")
            with open(xml_path, "w", encoding="utf-8") as f:
                f.write(xml)
            result = Command().load_xml(Path(xml_path))

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Genesis")
        self.assertEqual(result[0]["slug"], "genesis")
        self.assertEqual(
            result[0]["verses"][1]["text"],
            "And the earth was without form, and void; and darkness was upon the face of the deep.",
        )
        self.assertEqual(result[1]["name"], "John")
        self.assertEqual(result[1]["order"], 43)

    def test_import_kjv_command_sqlite_format(self):
        """The management command can import a full book from a KJV SQLite file."""
        from django.core.management import call_command
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "kjv.db")
            self._make_kjv_db(
                db_path,
                [
                    (43, 1, 1, "In the beginning was the Word."),
                    (43, 1, 2, "The same was in the beginning with God."),
                    (43, 3, 16, "For God so loved the world..."),
                ],
            )
            call_command(
                "import_kjv",
                file=db_path,
                format="sqlite",
                clear=True,
                verbosity=0,
            )

        self.assertEqual(BibleBook.objects.count(), 1)
        self.assertEqual(BibleVerse.objects.count(), 3)
        book = BibleBook.objects.get(slug="john")
        self.assertEqual(book.chapters, 21)

    def test_import_kjv_command_xml_updates_existing_sample_verses(self):
        """XML import should replace existing sample text and add missing verses."""
        from django.core.management import call_command

        xml = """<?xml version="1.0" encoding="utf-8"?>
<XMLBIBLE>
  <BIBLEBOOK bnumber="43" bname="John">
    <CHAPTER cnumber="3">
      <VERS vnumber="16">For God so loved the world.</VERS>
      <VERS vnumber="17">For God sent not his Son into the world.</VERS>
    </CHAPTER>
  </BIBLEBOOK>
</XMLBIBLE>
"""

        BibleBook.objects.all().delete()
        book = BibleBook.objects.create(
            name="John", slug="john", order=43, testament="NT", chapters=21
        )
        BibleVerse.objects.create(
            book=book, chapter=3, verse=16, text="stale sample text"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = os.path.join(tmpdir, "kjv.xml")
            with open(xml_path, "w", encoding="utf-8") as f:
                f.write(xml)
            call_command("import_kjv", file=xml_path, format="xml", verbosity=0)

        self.assertEqual(BibleBook.objects.count(), 1)
        self.assertEqual(BibleVerse.objects.count(), 2)
        self.assertEqual(
            BibleVerse.objects.get(book=book, chapter=3, verse=16).text,
            "For God so loved the world.",
        )
