from django.test import TestCase, Client
from django.urls import reverse
from bible.models import BibleBook, BibleVerse


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

