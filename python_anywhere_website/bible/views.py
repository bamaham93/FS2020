from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import BibleBook, BibleVerse


def book_list(request):
    """
    Display list of all Bible books, grouped by testament.
    /bible/
    """
    ot_books = BibleBook.objects.filter(testament="OT")
    nt_books = BibleBook.objects.filter(testament="NT")

    context = {
        "ot_books": ot_books,
        "nt_books": nt_books,
    }
    return render(request, "bible/book_list.html", context)


def chapter_list(request, book_slug):
    """
    Display list of chapters for a specific book.
    /bible/{book-slug}/
    """
    book = get_object_or_404(BibleBook, slug=book_slug)
    chapters = range(1, book.chapters + 1)

    context = {
        "book": book,
        "chapters": chapters,
    }
    return render(request, "bible/chapter_list.html", context)


def chapter_reader(request, book_slug, chapter):
    """
    Display a single chapter with all verses.
    /bible/{book-slug}/{chapter}/
    """
    book = get_object_or_404(BibleBook, slug=book_slug)

    # Validate chapter number
    if chapter < 1 or chapter > book.chapters:
        raise Http404("Chapter not found")

    verses = BibleVerse.objects.filter(book=book, chapter=chapter).select_related(
        "book"
    )

    # Determine prev/next chapter
    prev_chapter = None
    next_chapter = None

    if chapter > 1:
        prev_chapter = chapter - 1
        prev_book = book
    else:
        # Check for previous book
        prev_book_obj = BibleBook.objects.filter(order=book.order - 1).first()
        if prev_book_obj:
            prev_book = prev_book_obj
            prev_chapter = prev_book_obj.chapters

    if chapter < book.chapters:
        next_chapter = chapter + 1
        next_book = book
    else:
        # Check for next book
        next_book_obj = BibleBook.objects.filter(order=book.order + 1).first()
        if next_book_obj:
            next_book = next_book_obj
            next_chapter = 1

    context = {
        "book": book,
        "chapter": chapter,
        "verses": verses,
        "prev_chapter": prev_chapter,
        "prev_book": prev_book if prev_chapter else None,
        "next_chapter": next_chapter,
        "next_book": next_book if next_chapter else None,
    }
    return render(request, "bible/chapter_reader.html", context)


def continuous_reader(request, book_slug=None, chapter=1):
    """
    Display a continuous Bible reader that lazy-loads chapters while scrolling.
    /bible/reader/
    """
    books = list(BibleBook.objects.all())
    first_book = books[0] if books else None
    active_book = first_book

    if book_slug:
        active_book = next(
            (book for book in books if book.slug == book_slug), first_book
        )

    query_book = request.GET.get("book")
    if query_book:
        active_book = next(
            (book for book in books if book.slug == query_book), active_book
        )

    query_chapter = request.GET.get("chapter")
    if query_chapter and query_chapter.isdigit():
        chapter = int(query_chapter)

    if active_book:
        chapter = max(1, min(chapter, active_book.chapters))

    books_with_chapters = [
        {
            "slug": book.slug,
            "name": book.name,
            "chapter_count": book.chapters,
            "chapters": list(range(1, book.chapters + 1)),
        }
        for book in books
    ]

    context = {
        "books": books,
        "books_with_chapters": books_with_chapters,
        "initial_book": active_book,
        "initial_chapter": chapter,
    }
    return render(request, "bible/continuous_reader.html", context)
