from django.db import models


class BibleBook(models.Model):
    """
    Represents a book of the Bible (e.g., Genesis, John).
    66 books total (39 OT + 27 NT).
    """
    TESTAMENT_CHOICES = [
        ('OT', 'Old Testament'),
        ('NT', 'New Testament'),
    ]
    
    name = models.CharField(max_length=50, help_text="Book name (e.g., 'John')")
    slug = models.SlugField(max_length=50, unique=True, help_text="URL-friendly name (e.g., 'john')")
    order = models.PositiveIntegerField(unique=True, help_text="Book order (1-66)")
    testament = models.CharField(max_length=2, choices=TESTAMENT_CHOICES)
    chapters = models.PositiveIntegerField(default=1, help_text="Number of chapters in book")
    
    class Meta:
        ordering = ['order']
        app_label = 'bible'
        verbose_name = 'Bible Book'
        verbose_name_plural = 'Bible Books'
    
    def __str__(self):
        return self.name


class BibleVerse(models.Model):
    """
    Represents a single verse of Scripture.
    Unique constraint on (book, chapter, verse).
    """
    book = models.ForeignKey(BibleBook, on_delete=models.CASCADE, related_name='verses')
    chapter = models.PositiveIntegerField()
    verse = models.PositiveIntegerField()
    text = models.TextField(help_text="Full verse text")
    
    class Meta:
        ordering = ['book__order', 'chapter', 'verse']
        app_label = 'bible'
        unique_together = [['book', 'chapter', 'verse']]
        indexes = [
            models.Index(fields=['book', 'chapter']),
        ]
        verbose_name = 'Bible Verse'
        verbose_name_plural = 'Bible Verses'
    
    def __str__(self):
        return f"{self.book.name} {self.chapter}:{self.verse}"
