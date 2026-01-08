import logging
import threading
from django.contrib import admin
from django.contrib import messages
from django.core.management import call_command
from .models import BibleBook, BibleVerse

logger = logging.getLogger(__name__)


def run_kjv_import():
    """
    Helper function to run the KJV Bible import in a background thread.
    This function calls the import_kjv management command with the --clear flag
    to replace existing data.
    """
    try:
        logger.info("Starting KJV Bible import...")
        call_command("import_kjv", "--clear")
        logger.info("KJV Bible import completed successfully")
    except Exception as e:
        logger.error(f"KJV Bible import failed: {str(e)}", exc_info=True)


@admin.register(BibleBook)
class BibleBookAdmin(admin.ModelAdmin):
    list_display = ["order", "name", "slug", "testament", "chapters"]
    list_filter = ["testament"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]
    actions = ["import_kjv_bible"]

    def import_kjv_bible(self, request, queryset):
        """
        Admin action to import the KJV Bible.
        Runs the import in a background thread to avoid blocking the request.
        """
        try:
            # Start import in background thread (daemon=True allows clean shutdown)
            import_thread = threading.Thread(target=run_kjv_import, daemon=True)
            import_thread.start()

            messages.success(
                request,
                "KJV Bible import has been started in the background. "
                "Check the server logs for progress and completion status.",
            )
        except Exception as e:
            logger.error(f"Failed to start KJV Bible import: {str(e)}", exc_info=True)
            messages.error(request, f"Failed to start KJV Bible import: {str(e)}")

    import_kjv_bible.short_description = "Import KJV Bible"


@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ["book", "chapter", "verse", "text_preview"]
    list_filter = ["book", "chapter"]
    search_fields = ["text", "book__name"]
    ordering = ["book__order", "chapter", "verse"]

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_preview.short_description = "Text"
