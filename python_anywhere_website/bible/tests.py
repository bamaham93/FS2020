from django.test import TestCase, Client
from django.urls import reverse
from bible.models import BibleBook, BibleVerse
from bible.gutenberg_parser import parse_gutenberg_kjv, BOOK_INFO
import tempfile
import os


class GutenbergParserTest(TestCase):
    """Tests for the Gutenberg KJV parser."""
    
    def create_test_file(self, content):
        """Helper to create a temporary test file."""
        fd, path = tempfile.mkstemp(suffix='.txt')
        with os.fdopen(fd, 'w') as f:
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
            self.assertEqual(result[0]['name'], 'Genesis')
            self.assertEqual(len(result[0]['verses']), 3)
            self.assertEqual(result[0]['verses'][0]['chapter'], 1)
            self.assertEqual(result[0]['verses'][0]['verse'], 1)
            self.assertIn('beginning', result[0]['verses'][0]['text'])
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
            book_names = {book['name'] for book in result}
            # Should have all 4 books, no duplicates
            self.assertIn('1 Samuel', book_names)
            self.assertIn('2 Samuel', book_names)
            self.assertIn('1 Kings', book_names)
            self.assertIn('2 Kings', book_names)
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
            book_names = {book['name'] for book in result}
            self.assertIn('1 Chronicles', book_names)
            self.assertIn('2 Chronicles', book_names)
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
            verse1_text = result[0]['verses'][0]['text']
            # Should contain both lines joined
            self.assertIn('In the beginning', verse1_text)
            self.assertIn('Word was God', verse1_text)
        finally:
            os.unlink(path)
    
    def test_all_66_books_defined(self):
        """Test that BOOK_INFO has all 66 books."""
        self.assertEqual(len(BOOK_INFO), 66)
        # Check a few key books
        self.assertIn('Genesis', BOOK_INFO)
        self.assertIn('Revelation', BOOK_INFO)
        self.assertIn('1 Samuel', BOOK_INFO)
        self.assertIn('2 Kings', BOOK_INFO)
        self.assertIn('1 Chronicles', BOOK_INFO)


class BibleBookModelTest(TestCase):
    def setUp(self):
        self.book = BibleBook.objects.create(
            name='John',
            slug='john',
            order=43,
            testament='NT',
            chapters=21
        )

    def test_book_creation(self):
        self.assertEqual(self.book.name, 'John')
        self.assertEqual(self.book.slug, 'john')
        self.assertEqual(str(self.book), 'John')

    def test_book_ordering(self):
        genesis = BibleBook.objects.create(
            name='Genesis',
            slug='genesis',
            order=1,
            testament='OT',
            chapters=50
        )
        books = list(BibleBook.objects.all())
        self.assertEqual(books[0], genesis)
        self.assertEqual(books[1], self.book)


class BibleVerseModelTest(TestCase):
    def setUp(self):
        self.book = BibleBook.objects.create(
            name='John',
            slug='john',
            order=43,
            testament='NT',
            chapters=21
        )
        self.verse = BibleVerse.objects.create(
            book=self.book,
            chapter=3,
            verse=16,
            text='For God so loved the world...'
        )

    def test_verse_creation(self):
        self.assertEqual(self.verse.chapter, 3)
        self.assertEqual(self.verse.verse, 16)
        self.assertEqual(str(self.verse), 'John 3:16')

    def test_verse_unique_constraint(self):
        with self.assertRaises(Exception):
            BibleVerse.objects.create(
                book=self.book,
                chapter=3,
                verse=16,
                text='Duplicate verse'
            )


class BibleViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.book = BibleBook.objects.create(
            name='John',
            slug='john',
            order=43,
            testament='NT',
            chapters=21
        )
        self.verse1 = BibleVerse.objects.create(
            book=self.book,
            chapter=3,
            verse=16,
            text='For God so loved the world...'
        )
        self.verse2 = BibleVerse.objects.create(
            book=self.book,
            chapter=3,
            verse=17,
            text='For God sent not his Son...'
        )

    def test_book_list_view(self):
        response = self.client.get(reverse('bible:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John')
    
    def test_all_66_books_displayed(self):
        """Integration test: Verify all 66 books are displayed on the home page."""
        # Delete the book created in setUp to avoid conflicts
        BibleBook.objects.all().delete()
        
        # Create all 66 books from BOOK_INFO
        for book_name, (slug, order, testament, chapters) in BOOK_INFO.items():
            BibleBook.objects.create(
                name=book_name,
                slug=slug,
                order=order,
                testament=testament,
                chapters=chapters
            )
        
        # Verify we have exactly 66 books
        self.assertEqual(BibleBook.objects.count(), 66)
        
        # Get the Bible home page
        response = self.client.get(reverse('bible:index'))
        self.assertEqual(response.status_code, 200)
        
        # Verify all 66 books are in the response
        for book_name in BOOK_INFO.keys():
            with self.subTest(book=book_name):
                self.assertContains(response, book_name)
        
        # Verify the correct counts are shown
        self.assertContains(response, 'Old Testament')
        self.assertContains(response, 'New Testament')
        
        # Verify specific problematic books that were previously missing
        self.assertContains(response, '1 Samuel')
        self.assertContains(response, '2 Samuel')
        self.assertContains(response, '1 Kings')
        self.assertContains(response, '2 Kings')
        self.assertContains(response, '1 Chronicles')
        self.assertContains(response, '2 Chronicles')

    def test_chapter_list_view(self):
        response = self.client.get(reverse('bible:chapter_list', args=['john']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John')

    def test_chapter_reader_view(self):
        response = self.client.get(reverse('bible:chapter_reader', args=['john', 3]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'For God so loved the world')
        self.assertContains(response, 'v16')

    def test_invalid_chapter(self):
        response = self.client.get(reverse('bible:chapter_reader', args=['john', 999]))
        self.assertEqual(response.status_code, 404)


class BibleAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.book = BibleBook.objects.create(
            name='John',
            slug='john',
            order=43,
            testament='NT',
            chapters=21
        )
        self.verse = BibleVerse.objects.create(
            book=self.book,
            chapter=3,
            verse=16,
            text='For God so loved the world...'
        )

    def test_api_books(self):
        response = self.client.get('/api/v1/bible/books')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('books', data)
        self.assertEqual(len(data['books']), 1)
        self.assertEqual(data['books'][0]['name'], 'John')

    def test_api_chapter(self):
        response = self.client.get('/api/v1/bible/books/john/chapters/3')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['chapter'], 3)
        self.assertEqual(len(data['verses']), 1)
        self.assertEqual(data['verses'][0]['verse'], 16)

    def test_api_passage(self):
        response = self.client.get('/api/v1/bible/passage?ref=John+3:16')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['chapter'], 3)
        self.assertEqual(len(data['verses']), 1)
        self.assertEqual(data['verses'][0]['verse'], 16)

    def test_api_passage_invalid(self):
        response = self.client.get('/api/v1/bible/passage?ref=Invalid')
        self.assertEqual(response.status_code, 400)

    def test_api_rate_limit_headers(self):
        response = self.client.get('/api/v1/bible/books')
        self.assertEqual(response.status_code, 200)
        self.assertIn('X-RateLimit-Limit', response)
        self.assertIn('X-RateLimit-Remaining', response)
        self.assertEqual(response['X-RateLimit-Limit'], '100')


class AdminActionTest(TestCase):
    """Tests for admin actions."""

    def setUp(self):
        from django.contrib.auth.models import User
        from bible.admin import import_kjv_action, BibleBookAdmin
        
        self.user_staff = User.objects.create_user(
            username='staffuser',
            password='testpass',
            is_staff=True
        )
        self.user_nonstaff = User.objects.create_user(
            username='normaluser',
            password='testpass',
            is_staff=False
        )
        self.book = BibleBook.objects.create(
            name='John',
            slug='john',
            order=43,
            testament='NT',
            chapters=21
        )
        self.admin = BibleBookAdmin(BibleBook, None)

    def test_import_kjv_action_requires_staff(self):
        """Test that non-staff users cannot run the import action."""
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.test import RequestFactory
        from bible.admin import import_kjv_action

        factory = RequestFactory()
        request = factory.post('/admin/bible/biblebook/')
        request.user = self.user_nonstaff
        
        # Add message support to request
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        # Run the action
        queryset = BibleBook.objects.all()
        import_kjv_action(self.admin, request, queryset)

        # Check that an error message was sent
        message_list = list(messages)
        self.assertEqual(len(message_list), 1)
        self.assertIn('Only staff users', str(message_list[0]))

    def test_import_kjv_action_starts_thread_for_staff(self):
        """Test that staff users can start the import action."""
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.test import RequestFactory
        from bible.admin import import_kjv_action

        factory = RequestFactory()
        request = factory.post('/admin/bible/biblebook/')
        request.user = self.user_staff
        
        # Add message support to request
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        # Run the action
        queryset = BibleBook.objects.all()
        import_kjv_action(self.admin, request, queryset)

        # Check that a success message was sent
        message_list = list(messages)
        self.assertEqual(len(message_list), 1)
        self.assertIn('started in the background', str(message_list[0]))

    def test_import_kjv_action_metadata(self):
        """Test that the action has proper metadata."""
        from bible.admin import import_kjv_action

        self.assertEqual(import_kjv_action.short_description, "Import KJV Bible")
        self.assertEqual(import_kjv_action.allowed_permissions, ('change',))

    def test_admin_has_action_registered(self):
        """Test that BibleBookAdmin has the import action registered."""
        from bible.admin import BibleBookAdmin, import_kjv_action

        # Get the admin class
        admin = BibleBookAdmin(BibleBook, None)
        
        # Check that actions includes our import action
        self.assertIn(import_kjv_action, admin.actions)

