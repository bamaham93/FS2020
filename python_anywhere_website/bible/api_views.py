from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from .models import BibleBook, BibleVerse
from .decorators import rate_limit
import re


@require_GET
@cache_page(60 * 60 * 24)  # Cache for 24 hours
@rate_limit(key_prefix='bible_books', rate=100, per=60)
def api_books(request):
    """
    GET /api/v1/bible/books
    Returns list of all Bible books.
    """
    books = BibleBook.objects.all()
    data = {
        'books': [
            {
                'name': book.name,
                'slug': book.slug,
                'order': book.order,
                'testament': book.get_testament_display(),
                'chapters': book.chapters,
            }
            for book in books
        ]
    }
    response = JsonResponse(data)
    response['Cache-Control'] = 'public, max-age=86400'
    return response


@require_GET
@cache_page(60 * 60 * 24)  # Cache for 24 hours
@rate_limit(key_prefix='bible_chapter', rate=100, per=60)
def api_chapter(request, book_slug, chapter):
    """
    GET /api/v1/bible/books/{slug}/chapters/{chapter}
    Returns all verses for a specific chapter.
    """
    book = get_object_or_404(BibleBook, slug=book_slug)
    
    # Validate chapter
    if chapter < 1 or chapter > book.chapters:
        return JsonResponse({'error': 'Chapter not found'}, status=404)
    
    verses = BibleVerse.objects.filter(book=book, chapter=chapter).select_related('book')
    
    data = {
        'book': {
            'name': book.name,
            'slug': book.slug,
            'testament': book.get_testament_display(),
        },
        'chapter': chapter,
        'verses': [
            {
                'verse': verse.verse,
                'text': verse.text,
            }
            for verse in verses
        ]
    }
    response = JsonResponse(data)
    response['Cache-Control'] = 'public, max-age=86400'
    return response


@require_GET
@cache_page(60 * 60 * 24)  # Cache for 24 hours
@rate_limit(key_prefix='bible_passage', rate=100, per=60)
def api_passage(request):
    """
    GET /api/v1/bible/passage?ref=John+3:16-18
    Returns verses for a passage reference.
    Supports formats: "John 3", "John 3:16", "John 3:16-18"
    """
    ref = request.GET.get('ref', '').strip()
    
    if not ref:
        return JsonResponse({'error': 'Reference parameter required'}, status=400)
    
    # Parse the reference
    parsed = parse_reference(ref)
    
    if 'error' in parsed:
        return JsonResponse(parsed, status=400)
    
    book_name = parsed['book']
    chapter = parsed['chapter']
    start_verse = parsed.get('start_verse')
    end_verse = parsed.get('end_verse')
    
    # Find the book (case-insensitive)
    try:
        book = BibleBook.objects.get(name__iexact=book_name)
    except BibleBook.DoesNotExist:
        # Try by slug
        try:
            book = BibleBook.objects.get(slug__iexact=book_name.lower().replace(' ', '-'))
        except BibleBook.DoesNotExist:
            return JsonResponse({'error': f'Book "{book_name}" not found'}, status=404)
    
    # Validate chapter
    if chapter < 1 or chapter > book.chapters:
        return JsonResponse({'error': 'Chapter not found'}, status=404)
    
    # Build query
    query = BibleVerse.objects.filter(book=book, chapter=chapter)
    
    if start_verse is not None:
        query = query.filter(verse__gte=start_verse)
        if end_verse is not None:
            query = query.filter(verse__lte=end_verse)
        else:
            query = query.filter(verse=start_verse)
    
    verses = query.select_related('book')
    
    data = {
        'reference': ref,
        'normalized': f"{book.name} {chapter}" + (f":{start_verse}" if start_verse else "") + (f"-{end_verse}" if end_verse and end_verse != start_verse else ""),
        'book': {
            'name': book.name,
            'slug': book.slug,
        },
        'chapter': chapter,
        'verses': [
            {
                'verse': verse.verse,
                'text': verse.text,
            }
            for verse in verses
        ]
    }
    
    response = JsonResponse(data)
    response['Cache-Control'] = 'public, max-age=86400'
    return response


def parse_reference(ref):
    """
    Parse a Bible reference string.
    Supports: "John 3", "John 3:16", "John 3:16-18"
    Returns dict with book, chapter, start_verse (optional), end_verse (optional)
    """
    # Pattern: Book Chapter or Book Chapter:Verse or Book Chapter:Verse-Verse
    # Allow for book names with spaces (e.g., "1 John", "Song of Solomon")
    pattern = r'^([1-3]?\s*[A-Za-z\s]+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$'
    
    match = re.match(pattern, ref.strip())
    
    if not match:
        return {'error': 'Invalid reference format. Use: "Book Chapter" or "Book Chapter:Verse" or "Book Chapter:Verse-Verse"'}
    
    book_name = match.group(1).strip()
    chapter = int(match.group(2))
    start_verse = int(match.group(3)) if match.group(3) else None
    end_verse = int(match.group(4)) if match.group(4) else None
    
    result = {
        'book': book_name,
        'chapter': chapter,
    }
    
    if start_verse is not None:
        result['start_verse'] = start_verse
    
    if end_verse is not None:
        if end_verse < start_verse:
            return {'error': 'End verse must be greater than or equal to start verse'}
        result['end_verse'] = end_verse
    
    return result
