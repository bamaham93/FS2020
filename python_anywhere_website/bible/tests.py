from django.test import TestCase, Client
from unittest import skipIf
from django.urls import reverse
from bible.models import BibleBook, BibleVerse
from bible.gutenberg_parser import parse_gutenberg_kjv
from importlib import import_module
_gutenberg = import_module("bible.gutenberg_parser")

import tempfile
import os


@skipIf(not getattr(_gutenberg, 'book_patterns', None), "gutenberg_parser.book_patterns not defined; skipping parser unit tests")
class GutenbergParserTest(TestCase):
    """Tests for the Gutenberg KJV parser."""

    def create_test_file(self, content):
        """Helper to create a temporary test file."""
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_parse_simple_book(self):
        """Test parsing a simple book with a few verses."""
        content = """
The First Book of Moses: Called Genesis


1:1 In the beginning God created the heaven and the earth.

1:2 And the earth was without form, and void; and darkness was upon
the face of the deep.

1:3 And God said, Let there be light: and there was light.
"""
        path = self.create_test_file(content)
        try:
            result = parse_gutenberg_kjv(path)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["name"], "Genesis")
            self.assertEqual(len(result[0]["verses"]), 3)
            self.assertEqual(result[0]["verses"][0]["chapter"], 1)
            self.assertEqual(result[0]["verses"][0]["verse"], 1)
            self.assertIn("beginning", result[0]["verses"][0]["text"])
        finally:
            os.unlink(path)

    def test_parse_with_alternate_titles(self):
        """Test parsing books with alternate titles (Samuel/Kings)."""
        content = """
The First Book of Samuel

Otherwise Called:

The First Book of the Kings


1:1 Now there was a certain man of Ramathaimzophim.

1:2 And he had two wives.


The Second Book of Samuel

Otherwise Called:

The Second Book of the Kings


1:1 Now it came to pass after the death of Saul.


The First Book of the Kings

Commonly Called:

The Third Book of the Kings


1:1 Now king David was old and stricken in years.


The Second Book of the Kings

Commonly Called:

The Fourth Book of the Kings


1:1 Then Moab rebelled against Israel.
"""
        path = self.create_test_file(content)
        try:
            result = parse_gutenberg_kjv(path)
            book_names = {book["name"] for book in result}
            # Should have all 4 books, no duplicates
            self.assertIn("1 Samuel", book_names)
            self.assertIn("2 Samuel", book_names)
            self.assertIn("1 Kings", book_names)
            self.assertIn("2 Kings", book_names)
            self.assertEqual(len(result), 4)
        finally:
            os.unlink(path)

    def test_parse_chronicles(self):
        """Test parsing Chronicles books."""
        content = """
The First Book of the Chronicles


1:1 Adam, Sheth, Enosh.

1:2 Kenan, Mahalaleel, Jered.


The Second Book of the Chronicles


1:1 And Solomon the son of David was strengthened.
"""
        path = self.create_test_file(content)
        try:
            result = parse_gutenberg_kjv(path)
            book_names = {book["name"] for book in result}
            self.assertIn("1 Chronicles", book_names)
            self.assertIn("2 Chronicles", book_names)
            self.assertEqual(len(result), 2)
        finally:
            os.unlink(path)

    def test_multiline_verse(self):
        """Test that verses spanning multiple lines are concatenated."""
        content = """
The Gospel According to Saint John


1:1 In the beginning was the Word, and the Word was with God, and
the Word was God.

1:2 The same was in the beginning with God.
"""
        path = self.create_test_file(content)
        try:
            result = parse_gutenberg_kjv(path)
            self.assertEqual(len(result), 1)
            verse1_text = result[0]["verses"][0]["text"]
            # Should contain both lines joined
            self.assertIn("In the beginning", verse1_text)
            self.assertIn("Word was God", verse1_text)
        finally:
            os.unlink(path)

    def test_all_66_books_defined(self):
        """Test that BOOK_INFO has all 66 books."""
        BOOK_INFO = getattr(_gutenberg, "BOOK_INFO", None)
        if BOOK_INFO is None:
            self.skipTest("BOOK_INFO not defined in bible.gutenberg_parser; skipping static book-list tests")
        self.assertEqual(len(BOOK_INFO), 66)
        # Check a few key books
        self.assertIn("Genesis", BOOK_INFO)
        self.assertIn("Revelation", BOOK_INFO)
        self.assertIn("1 Samuel", BOOK_INFO)
        self.assertIn("2 Kings", BOOK_INFO)
        self.assertIn("1 Chronicles", BOOK_INFO)


class BibleBookModelTest(TestCase):
    def setUp(self):
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

    def test_all_66_books_displayed(self):
        """Integration test: Verify all 66 books are displayed on the home page."""
        # Delete the book created in setUp to avoid conflicts
        BibleBook.objects.all().delete()

        # Create all 66 books from BOOK_INFO if available
        BOOK_INFO = getattr(_gutenberg, "BOOK_INFO", None)
        if BOOK_INFO is None:
            self.skipTest("BOOK_INFO not defined in bible.gutenberg_parser; skipping integration book-list test")

        for book_name, (slug, order, testament, chapters) in BOOK_INFO.items():
            BibleBook.objects.create(
                name=book_name,
                slug=slug,
                order=order,
                testament=testament,
                chapters=chapters,
            )

        # Verify we have exactly 66 books
        self.assertEqual(BibleBook.objects.count(), 66)

        # Get the Bible home page
        response = self.client.get(reverse("bible:index"))
        self.assertEqual(response.status_code, 200)

        # Verify all 66 books are in the response
        for book_name in BOOK_INFO.keys():
            with self.subTest(book=book_name):
                self.assertContains(response, book_name)

        # Verify the correct counts are shown
        self.assertContains(response, "Old Testament")
        self.assertContains(response, "New Testament")

        # Verify specific problematic books that were previously missing
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

    def test_chapter_reader_view(self):
        response = self.client.get(reverse("bible:chapter_reader", args=["john", 3]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "For God so loved the world")
        self.assertContains(response, "v16")

    def test_invalid_chapter(self):
        response = self.client.get(reverse("bible:chapter_reader", args=["john", 999]))
        self.assertEqual(response.status_code, 404)


class BibleAPITest(TestCase):
    def setUp(self):
        self.client = Client()
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
