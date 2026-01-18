from django.contrib import admin, messages
from django.core.management import call_command
from .models import BibleBook, BibleVerse
import threading
import logging

logger = logging.getLogger(__name__)


def _run_import_kjv(caller_name=None):
    """
    Helper that runs the management command. Intended to run in a background thread.
    """
    try:
        logger.info("Admin-initiated KJV import started (user=%s)", caller_name)
        # Call the management command; use keyword arg for the --clear flag
        call_command('import_kjv', clear=True)
        logger.info("Admin-initiated KJV import completed (user=%s)", caller_name)
    except Exception:
        logger.exception("Admin-initiated KJV import failed (user=%s)", caller_name)


def import_kjv_action(modeladmin, request, queryset):
    """
    Admin action to start the KJV import in a background thread.
    - Visible in the actions dropdown on the BibleBook changelist.
    - Uses standard admin permissions (requires change permission).
    - Starts the import in a daemon thread and returns immediately.
    """
    # Limit to staff users as a safety check (admin actions normally require appropriate perms)
    if not request.user.is_staff:
        modeladmin.message_user(request, "Only staff users may run the KJV import.", level=messages.ERROR)
        return

    caller = getattr(request.user, 'username', str(request.user))
    try:
        thread = threading.Thread(target=_run_import_kjv, args=(caller,), daemon=True)
        thread.start()
        modeladmin.message_user(
            request,
            "KJV import has been started in the background. Check the server logs for progress and errors.",
            level=messages.INFO,
        )
    except Exception as exc:
        logger.exception("Failed to start KJV import thread (user=%s)", caller)
        modeladmin.message_user(request, f"Failed to start import: {exc}", level=messages.ERROR)


# Action metadata for admin UI
import_kjv_action.short_description = "Import KJV Bible"
import_kjv_action.allowed_permissions = ('change',)


@admin.register(BibleBook)
class BibleBookAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'slug', 'testament', 'chapters']
    list_filter = ['testament']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order']

    # Register the import action on the changelist actions dropdown
    actions = [import_kjv_action]


@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ['book', 'chapter', 'verse', 'text_preview']
    list_filter = ['book', 'chapter']
    search_fields = ['text', 'book__name']
    ordering = ['book__order', 'chapter', 'verse']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'