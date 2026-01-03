from django.contrib import admin
from .models import BibleBook, BibleVerse


@admin.register(BibleBook)
class BibleBookAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'slug', 'testament', 'chapters']
    list_filter = ['testament']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order']


@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ['book', 'chapter', 'verse', 'text_preview']
    list_filter = ['book', 'chapter']
    search_fields = ['text', 'book__name']
    ordering = ['book__order', 'chapter', 'verse']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'
