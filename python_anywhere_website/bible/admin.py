from django.contrib import admin
from django.contrib import messages
from django.core.management import call_command
from .models import BibleBook, BibleVerse
import threading
import logging

logger = logging.getLogger(__name__)


def _run_import_in_background():
    """
    Helper function to run the KJV import in a background thread.
    Executes the import_kjv management command with --clear flag.
    Logs any exceptions that occur during import.
    """
    try:
        logger.info("Starting KJV Bible import in background thread")
        call_command("import_kjv", "--clear")
        logger.info("KJV Bible import completed successfully")
    except Exception as e:
        logger.error(f"Error during KJV Bible import: {e}", exc_info=True)


@admin.action(description="Import KJV Bible (replaces existing data)")
def import_kjv_bible_action(modeladmin, request, queryset):
    """
    Admin action to import the KJV Bible data.
    Runs the import_kjv management command in a background thread
    to avoid blocking the admin interface.

    This action is available to staff users with change permission
    on the BibleBook model (standard admin action permission behavior).
    """
    try:
        # Start the import in a background thread
        import_thread = threading.Thread(target=_run_import_in_background, daemon=True)
        import_thread.start()

        messages.success(
            request,
            "KJV Bible import has been started in the background. "
            "This may take a few minutes. Check the server logs for progress.",
        )
    except Exception as e:
        logger.error(f"Failed to start KJV Bible import: {e}", exc_info=True)
        messages.error(request, f"Failed to start KJV Bible import: {e}")


@admin.register(BibleBook)
class BibleBookAdmin(admin.ModelAdmin):
    list_display = ["order", "name", "slug", "testament", "chapters"]
    list_filter = ["testament"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]
    actions = [import_kjv_bible_action]


@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ["book", "chapter", "verse", "text_preview"]
    list_filter = ["book", "chapter"]
    search_fields = ["text", "book__name"]
    ordering = ["book__order", "chapter", "verse"]

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_preview.short_description = "Text"
