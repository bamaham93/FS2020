from django.contrib import admin, messages
from django.core.management import call_command
from .models import BibleBook, BibleVerse
import threading
import logging

logger = logging.getLogger(__name__)


def _run_import_kjv(caller_name=None):
    """
    Run the import_kjv management command with --clear flag.

    Catches all exceptions to prevent thread crashes and logs them.
    Broad exception handling is intentional - we want to catch and log
    any error that occurs during import (CommandError, DB errors, etc.).
    """
    try:
        logger.info("Admin-initiated KJV import started (user=%s)", caller_name)
        call_command("import_kjv", clear=True)
        logger.info("Admin-initiated KJV import completed (user=%s)", caller_name)
    except Exception:
        # Log full traceback for debugging. Broad exception handling is intentional.
        logger.exception("Admin-initiated KJV import failed (user=%s)", caller_name)


def import_kjv_action(modeladmin, request, queryset):
    """
    Admin action to trigger KJV Bible import in a background thread.

    WARNING: This action clears all existing Bible data before importing.

    Uses a daemon thread to avoid blocking the HTTP request. While daemon threads
    may be terminated if the process exits, this is acceptable for this use case
    since the import command is idempotent and can be re-run if needed.
    For production environments with high reliability requirements, consider
    using a task queue like Celery instead.
    """
    if not request.user.is_staff:
        modeladmin.message_user(
            request, "Only staff users may run the KJV import.", level=messages.ERROR
        )
        return

    caller = getattr(request.user, "username", str(request.user))
    try:
        # Daemon thread allows the request to complete without waiting for import
        thread = threading.Thread(target=_run_import_kjv, args=(caller,), daemon=True)
        thread.start()
        modeladmin.message_user(
            request,
            "KJV import has been started in the background. Check the server logs for progress and errors.",
            level=messages.INFO,
        )
    except Exception as exc:
        logger.exception("Failed to start KJV import thread (user=%s)", caller)
        modeladmin.message_user(
            request, f"Failed to start import: {exc}", level=messages.ERROR
        )


import_kjv_action.short_description = "Import KJV Bible"
import_kjv_action.allowed_permissions = ("change",)


@admin.register(BibleBook)
class BibleBookAdmin(admin.ModelAdmin):
    list_display = ["order", "name", "slug", "testament", "chapters"]
    list_filter = ["testament"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]
    actions = [import_kjv_action]


@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ["book", "chapter", "verse", "text_preview"]
    list_filter = ["book", "chapter"]
    search_fields = ["text", "book__name"]
    ordering = ["book__order", "chapter", "verse"]

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_preview.short_description = "Text"
