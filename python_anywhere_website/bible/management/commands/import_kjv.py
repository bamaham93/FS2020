from django.core.management.base import BaseCommand
from bible.models import BibleBook, BibleVerse


class Command(BaseCommand):
    help = 'Import KJV Bible data into the database'

    def handle(self, *args, **options):
        self.stdout.write('Importing KJV Bible data...')
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        BibleVerse.objects.all().delete()
        BibleBook.objects.all().delete()
        
        # Sample data structure - In production, this would load from a file
        # For now, I'll create a minimal dataset for testing
        bible_data = self.get_sample_data()
        
        # Import books
        self.stdout.write('Creating books...')
        for book_data in bible_data:
            book = BibleBook.objects.create(
                name=book_data['name'],
                slug=book_data['slug'],
                order=book_data['order'],
                testament=book_data['testament'],
                chapters=book_data['chapters']
            )
            
            # Import verses for this book
            self.stdout.write(f'  Importing verses for {book.name}...')
            verses_to_create = []
            for verse_data in book_data['verses']:
                verses_to_create.append(
                    BibleVerse(
                        book=book,
                        chapter=verse_data['chapter'],
                        verse=verse_data['verse'],
                        text=verse_data['text']
                    )
                )
            
            BibleVerse.objects.bulk_create(verses_to_create)
            self.stdout.write(f'    Imported {len(verses_to_create)} verses')
        
        total_books = BibleBook.objects.count()
        total_verses = BibleVerse.objects.count()
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully imported {total_books} books and {total_verses} verses'
        ))

    def get_sample_data(self):
        """
        Returns sample Bible data for testing.
        In production, this would load from Project Gutenberg KJV text.
        """
        return [
            {
                'name': 'Genesis',
                'slug': 'genesis',
                'order': 1,
                'testament': 'OT',
                'chapters': 50,
                'verses': [
                    {
                        'chapter': 1,
                        'verse': 1,
                        'text': 'In the beginning God created the heaven and the earth.'
                    },
                    {
                        'chapter': 1,
                        'verse': 2,
                        'text': 'And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.'
                    },
                    {
                        'chapter': 1,
                        'verse': 3,
                        'text': 'And God said, Let there be light: and there was light.'
                    },
                ]
            },
            {
                'name': 'John',
                'slug': 'john',
                'order': 43,
                'testament': 'NT',
                'chapters': 21,
                'verses': [
                    {
                        'chapter': 1,
                        'verse': 1,
                        'text': 'In the beginning was the Word, and the Word was with God, and the Word was God.'
                    },
                    {
                        'chapter': 1,
                        'verse': 2,
                        'text': 'The same was in the beginning with God.'
                    },
                    {
                        'chapter': 3,
                        'verse': 16,
                        'text': 'For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.'
                    },
                    {
                        'chapter': 3,
                        'verse': 17,
                        'text': 'For God sent not his Son into the world to condemn the world; but that the world through him might be saved.'
                    },
                ]
            },
            {
                'name': 'Revelation',
                'slug': 'revelation',
                'order': 66,
                'testament': 'NT',
                'chapters': 22,
                'verses': [
                    {
                        'chapter': 1,
                        'verse': 1,
                        'text': 'The Revelation of Jesus Christ, which God gave unto him, to shew unto his servants things which must shortly come to pass; and he sent and signified it by his angel unto his servant John:'
                    },
                    {
                        'chapter': 22,
                        'verse': 21,
                        'text': 'The grace of our Lord Jesus Christ be with you all. Amen.'
                    },
                ]
            },
        ]
