from django.test import TestCase, Client
from django.urls import reverse
from bible.models import BibleBook, BibleVerse


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
